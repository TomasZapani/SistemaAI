package calendar

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

type CalendarListRequest struct {
	Day string `json:"day"`
}

type CalendarCreateRequest struct {
	Summary     string `json:"summary"`
	ClientName  string `json:"client_name"`
	ClientPhone string `json:"client_phone"`
	StartTime   string `json:"start_time"`
	EndTime     string `json:"end_time"`
	Description string `json:"description"`
}

type CalendarUpdateRequest struct {
	EventID     string `json:"event_id"`
	Summary     string `json:"summary"`
	ClientName  string `json:"client_name"`
	ClientPhone string `json:"client_phone"`
	StartTime   string `json:"start_time"`
	EndTime     string `json:"end_time"`
	Description string `json:"description"`
}

type CalendarDeleteRequest struct {
	EventID string `json:"event_id"`
}

type CalendarSearchRequest struct {
	ClientPhone string `json:"client_phone"`
}

func calendarPost(path string, payload any) ([]byte, error) {
	apiURL := os.Getenv("AGENT_API") + path

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

func CalendarList(payload *CalendarListRequest) ([]byte, error) {
	return calendarPost("/api/calendar/list", payload)
}

func CalendarCreate(payload *CalendarCreateRequest) ([]byte, error) {
	return calendarPost("/api/calendar/create", payload)
}

func CalendarUpdate(payload *CalendarUpdateRequest) ([]byte, error) {
	return calendarPost("/api/calendar/update", payload)
}

func CalendarDelete(payload *CalendarDeleteRequest) ([]byte, error) {
	return calendarPost("/api/calendar/delete", payload)
}

func CalendarSearch(payload *CalendarSearchRequest) ([]byte, error) {
	return calendarPost("/api/calendar/search", payload)
}
