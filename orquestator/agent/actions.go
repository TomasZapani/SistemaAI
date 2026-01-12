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

type CalendarListData struct {
	TimeMin    string `json:"time_min"`
	TimeMax    string `json:"time_max"`
	MaxResults int    `json:"max_results"`
}

type CalendarCreateData struct {
	Summary      string `json:"summary"`
	StartRFC3339 string `json:"start_rfc3339"`
	EndRFC3339   string `json:"end_rfc3339"`
	Description  string `json:"description"`
	Timezone     string `json:"timezone"`
}

type CalendarUpdateData struct {
	EventID      string  `json:"event_id"`
	Summary      *string `json:"summary"`
	StartRFC3339 *string `json:"start_rfc3339"`
	EndRFC3339   *string `json:"end_rfc3339"`
	Description  *string `json:"description"`
	Timezone     string  `json:"timezone"`
}

type CalendarDeleteData struct {
	EventID string `json:"event_id"`
}
