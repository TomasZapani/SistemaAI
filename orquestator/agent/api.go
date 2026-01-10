package agent

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

func StartSession(callSid string) (*AgentResponse, error) {
	apiURL := os.Getenv("LLM_URL") + "/api/start"
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

func Send(callSid string, message string) (*AgentResponse, error) {
	apiURL := os.Getenv("LLM_URL") + "/api/send"
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

func Context(callSid string, context string) (*AgentResponse, error) {
	apiURL := os.Getenv("LLM_URL") + "/api/context"
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

func EndSession(callSid string) error {
	apiURL := os.Getenv("LLM_URL") + "/api/end"
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
