package agent

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
)

type AppointmentData struct {
	Name  string `json:"name"`
	Date  string `json:"date"`
	Time  string `json:"time"`
	Notes string `json:"notes"`
}

type AgentResponse struct {
	Action  string          `json:"action"`
	Message string          `json:"message"`
	Data    AppointmentData `json:"data"`
}

func Query(callSid string, userMessage string) (*AgentResponse, error) {
	apiURL := os.Getenv("LLM_URL") + "/api/query"
	params := url.Values{}
	params.Add("call_sid", callSid)
	params.Add("user_message", userMessage)

	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())

	resp, err := http.Post(fullURL, "application/json", nil)
	if err != nil {
		return nil, fmt.Errorf("Error calling LLM query endpoint: %v", err)
	}
	defer resp.Body.Close()

	var agentResponse AgentResponse
	if err := json.NewDecoder(resp.Body).Decode(&agentResponse); err != nil {
		return nil, fmt.Errorf("Error parsing JSON: %v", err)
	}

	return &agentResponse, nil
}

func End(callSid string) error {
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
