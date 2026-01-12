package agent

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
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

func calendarPost(path string, payload any) ([]byte, error) {
	apiURL := os.Getenv("LLM_URL") + path

	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(apiURL, "application/json", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("Error calling calendar endpoint: %v", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("Calendar endpoint returned %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

func CalendarList(payload *CalendarListData) ([]byte, error) {
	return calendarPost("/api/calendar/list", payload)
}

func CalendarCreate(payload *CalendarCreateData) ([]byte, error) {
	return calendarPost("/api/calendar/create", payload)
}

func CalendarUpdate(payload *CalendarUpdateData) ([]byte, error) {
	return calendarPost("/api/calendar/update", payload)
}

func CalendarDelete(payload *CalendarDeleteData) ([]byte, error) {
	return calendarPost("/api/calendar/delete", payload)
}
