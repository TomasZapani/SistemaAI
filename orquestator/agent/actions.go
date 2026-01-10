package agent

type TalkData struct {
	Message string `json:"message"`
}

type CreateAppointmentData struct {
	Name  string `json:"name"`
	Date  string `json:"date"`
	Time  string `json:"time"`
	Notes string `json:"notes"`
}
