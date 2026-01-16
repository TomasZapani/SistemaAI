package appointment

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

type AppointmentListRequest struct {
	Day string `json:"day"`
}

type AppointmentCreateRequest struct {
	Summary     string `json:"summary"`
	ClientName  string `json:"client_name"`
	ClientPhone string `json:"client_phone"`
	StartTime   string `json:"start_time"`
	EndTime     string `json:"end_time"`
	Description string `json:"description"`
}

type AppointmentUpdateRequest struct {
	ID          string `json:"id"`
	Summary     string `json:"summary"`
	ClientName  string `json:"client_name"`
	ClientPhone string `json:"client_phone"`
	StartTime   string `json:"start_time"`
	EndTime     string `json:"end_time"`
	Description string `json:"description"`
}

type AppointmentDeleteRequest struct {
	ID string `json:"id"`
}

type AppointmentSearchRequest struct {
	ClientPhone string `json:"client_phone"`
}

func appointmentPost(path string, payload any) ([]byte, error) {
	apiURL := os.Getenv("AGENT_API") + path

	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(apiURL, "application/json", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("Error calling appointment endpoint: %v", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("Appointment endpoint returned %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

func AppointmentList(payload *AppointmentListRequest) ([]byte, error) {
	return appointmentPost("/api/appointment/list", payload)
}

func AppointmentCreate(payload *AppointmentCreateRequest) ([]byte, error) {
	return appointmentPost("/api/appointment/create", payload)
}

func AppointmentUpdate(payload *AppointmentUpdateRequest) ([]byte, error) {
	return appointmentPost("/api/appointment/update", payload)
}

func AppointmentDelete(payload *AppointmentDeleteRequest) ([]byte, error) {
	return appointmentPost("/api/appointment/delete", payload)
}

func AppointmentSearch(payload *AppointmentSearchRequest) ([]byte, error) {
	return appointmentPost("/api/appointment/search", payload)
}
