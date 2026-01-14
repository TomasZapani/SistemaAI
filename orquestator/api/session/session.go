package session

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
)

type AgentResponse struct {
	Action string          `json:"action"`
	Data   json.RawMessage `json:"data"`
}

// Starts a new session using a callSid
func Start(callSid string) (*AgentResponse, error) {
	apiURL := os.Getenv("AGENT_API") + "/api/session/start"
	params := url.Values{}
	params.Add("call_sid", callSid)

	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())

	resp, err := http.Post(fullURL, "application/json", nil)
	if err != nil {
		return nil, fmt.Errorf("Error calling LLM endpoint: %v", err)
	}
	defer resp.Body.Close()

	var agentResponse AgentResponse
	if err := json.NewDecoder(resp.Body).Decode(&agentResponse); err != nil {
		return nil, fmt.Errorf("Error parsing JSON: %v", err)
	}

	return &agentResponse, nil
}

// Send message to the session as a User
func Send(callSid string, message string) (*AgentResponse, error) {
	apiURL := os.Getenv("AGENT_API") + "/api/session/send"
	params := url.Values{}
	params.Add("call_sid", callSid)
	params.Add("message", message)

	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())

	resp, err := http.Post(fullURL, "application/json", nil)
	if err != nil {
		return nil, fmt.Errorf("Error calling LLM endpoint: %v", err)
	}
	defer resp.Body.Close()

	var agentResponse AgentResponse
	if err := json.NewDecoder(resp.Body).Decode(&agentResponse); err != nil {
		return nil, fmt.Errorf("Error parsing JSON: %v", err)
	}

	return &agentResponse, nil
}

// Adds context for the model
func Context(callSid string, context string) (*AgentResponse, error) {
	apiURL := os.Getenv("AGENT_API") + "/api/session/context"
	params := url.Values{}
	params.Add("call_sid", callSid)
	params.Add("context", context)

	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())

	resp, err := http.Post(fullURL, "application/json", nil)
	if err != nil {
		return nil, fmt.Errorf("Error calling LLM endpoint: %v", err)
	}
	defer resp.Body.Close()

	var agentResponse AgentResponse
	if err := json.NewDecoder(resp.Body).Decode(&agentResponse); err != nil {
		return nil, fmt.Errorf("Error parsing JSON: %v", err)
	}

	return &agentResponse, nil
}

// Ends and delete a existing session
func End(callSid string) error {
	apiURL := os.Getenv("AGENT_API") + "/api/session/end"
	params := url.Values{}
	params.Add("call_sid", callSid)

	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())

	req, err := http.NewRequest(http.MethodDelete, fullURL, nil)
	if err != nil {
		return err
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	return nil
}
