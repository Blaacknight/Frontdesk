import time
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta, timezone
import asyncio
import os

# --- LiveKit Imports (Fixed) ---
from livekit.agents import JobContext, Worker, WorkerOptions
from livekit.protocol.agent import JobType
from livekit.agents.llm import ChatContext, ChatMessage, ChatRole
import livekit.rtc as rtc

# --- Configuration ---
# These values will be used to tell you which environment variables to set.

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json"
REQUEST_TIMEOUT_MINUTES = 2
# --- End Configuration ---


class AIAgent:
    """
    AI Agent for Frontdesk.
    This class is SYNCHRONOUS. It connects to Firestore to:
    1. Check the knowledge_base for answers.
    2. Escalate to a supervisor (create a help_request) if the answer is unknown.
    3. Check for and mark timed-out requests.
    """
    
    def __init__(self, key_path):
        try:
            cred = credentials.Certificate(key_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase connection successful.")
        except ValueError:
            self.db = firestore.client()
            print("✅ Firebase connection re-established.")
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            print(f"Please ensure '{SERVICE_ACCOUNT_KEY_PATH}' is in the same directory.")
            exit(1)
            
        self.kb_ref = self.db.collection('knowledge_base')
        self.requests_ref = self.db.collection('help_requests')

    def check_for_timeouts(self):
        """
        SYNCHRONOUSLY finds and marks any 'pending' requests that are older
        than our defined timeout period.
        """
        print(f"⏳ [Agent] Checking for requests older than {REQUEST_TIMEOUT_MINUTES} minutes...")
        
        try:
            timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=REQUEST_TIMEOUT_MINUTES)
            
            # Use the modern FieldFilter syntax to avoid warnings
            query = self.requests_ref.where(
                filter=firestore.FieldFilter('status', '==', 'pending')
            ).where(
                filter=firestore.FieldFilter('createdAt', '<', timeout_threshold)
            )
            
            # This is now a SYNCHRONOUS stream
            timed_out_requests = query.stream()
            
            batch = self.db.batch()
            count = 0
            
            # Use a standard 'for' loop
            for request_doc in timed_out_requests:
                count += 1
                print(f"  -> Found timed-out request: {request_doc.id}")
                request_ref = self.requests_ref.document(request_doc.id)
                batch.update(request_ref, {
                    'status': 'unresolved_timeout'
                })
                
            if count > 0:
                batch.commit()
                print(f"✅ [Agent] Marked {count} requests as 'unresolved_timeout'.")
            else:
                print("👍 [Agent] No timed-out requests found.")
                
        except Exception as e:
            print(f"❌ [Agent] Error checking for timeouts: {e}")
            if "requires an index" in str(e):
                print("🚨🚨🚨 IMPORTANT: Your query requires a Firestore Index.")
                print("   Stop the script (Ctrl+C), copy the URL from the error,")
                print("   and paste it in your browser to create the index.")

    def lookup_knowledge(self, query_text):
        """
        SYNCHRONOUSLY searches the knowledge_base for a matching query.
        """
        print(f"🧠 [Agent] Searching knowledge base for: '{query_text}'")
        
        # Use FieldFilter for the query
        query_stream = self.kb_ref.where(
            filter=firestore.FieldFilter('query', '==', query_text)
        ).limit(1).stream()
        
        results = [doc.to_dict() for doc in query_stream]
        
        if results:
            answer = results[0].get('answer')
            print(f"💡 [Agent] Knowledge found! (Fast query)")
            return answer

        # Fallback for case-insensitive match (this is less efficient)
        all_knowledge_stream = self.kb_ref.stream() # <-- Fixed a typo here (was self.kb_)
        for doc in all_knowledge_stream:
            entry = doc.to_dict()
            if entry.get('query', '').lower() == query_text.lower():
                print(f"💡 [Agent] Knowledge found! (Case-insensitive fallback)")
                return entry.get('answer')
                
        print("❓ [Agent] Knowledge not found.")
        return None

    def escalate_to_supervisor(self, query_text, customer_id="cust_123"):
        """
        SYNCHRONOUSLY creates a new 'help_requests' document in Firestore.
        """
        print(f"🔥 [Agent] Escalating to supervisor for query: '{query_text}'")
        
        try:
            request_ref = self.requests_ref.document()
            
            new_request = {
                'customerId': customer_id,
                'customerQuery': query_text,
                'status': 'pending',
                'createdAt': firestore.SERVER_TIMESTAMP,
                'supervisorResponse': None,
                'resolvedAt': None,
                'notifiedCustomer': False
            }
            
            request_ref.set(new_request) 
            
            print(f"✅ [Agent] Help request created successfully (ID: {request_ref.id}).")
            return request_ref.id
            
        except Exception as e:
            print(f"❌ [Agent] Error creating help request: {e}")
            return None


# --- LIVEKIT WORKER SECTION (This part stays ASYC) ---

async def on_chat_received(ctx: JobContext, chat: ChatContext, agent: AIAgent):
    """
    This function is called when a new chat message is received.
    It calls the SYNCHRONOUS methods on the agent.
    """
    msg = await chat.messages.get() 
    query_text = msg.text
    print(f"\n📞 [LiveKit] Received call (chat) from user: '{query_text}'")

    # Call the SYNC function (no 'await')
    answer = agent.lookup_knowledge(query_text) 
    
    if answer:
        response_text = f"I found the answer for you! Here it is: {answer}"
        print(f"💬 [Agent] Responding: '{response_text}'")
        await chat.send_message(response_text)
    else:
        response_text = "That's a great question. Let me check with my supervisor and get back to you shortly."
        print(f"💬 [Agent] Responding: '{response_text}'")
        await chat.send_message(response_text)
        
        # Call the SYNC function (no 'await')
        agent.escalate_to_supervisor(query_text)
    
    print("📞 [LiveKit] Call (chat) handled.")

async def main(agent: AIAgent):
    """
    Main function to run the LiveKit worker (for old SDK versions).
    """
    print("🚀 [LiveKit] Starting worker...")

    async def on_job(ctx: JobContext):
        if ctx.job.type == JobType.AGENT:
            await on_chat_received(ctx, ctx.chat, agent)

    # Old versions expect credentials here directly
    worker_opts = WorkerOptions(
        entrypoint_fnc=on_job,
        ws_url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET
    )

    worker = Worker(worker_opts)

    # Optional networking fix for Windows
    if os.name == 'nt':
        try:
            worker._http_server._host = '127.0.0.1'
            print("✅ [Agent] Applied networking patch for Windows.")
        except Exception as e:
            print(f"⚠️ [Agent] Could not apply networking patch: {e}")

    print("✅ [LiveKit] Worker started. Waiting for calls (chat messages)...")
    await worker.run()


# --- Main execution ---
if __name__ == "__main__":
    
    # --- Environment Variable Check ---
    # We no longer need this check, as we are passing credentials
    # directly to the Worker.
        
    print("Initializing AI Agent...")
    agent = AIAgent(SERVICE_ACCOUNT_KEY_PATH)
    
    # Run the SYNC timeout check BEFORE starting the async loop
    agent.check_for_timeouts() 
    
    try:
        asyncio.run(main(agent))
    except KeyboardInterrupt:
        print("\n👋 [LiveKit] Worker shutting down.")

