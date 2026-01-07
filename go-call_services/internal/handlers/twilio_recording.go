package handlers

import (
	"bytes"
	"io"
	"mime/multipart"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

func TwilioHandleRecording(c *fiber.Ctx) error {

	recordingURL := c.FormValue("RecordingUrl")
	if recordingURL == "" {
		return c.SendStatus(400)
	}

	// 1️⃣ Descargar audio
	resp, err := http.Get(recordingURL + ".wav")
	if err != nil {
		return c.SendStatus(500)
	}
	defer resp.Body.Close()

	audioBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return c.SendStatus(500)
	}

	// 2️⃣ Crear multipart/form-data
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("file", "recording.wav")
	if err != nil {
		return c.SendStatus(500)
	}

	_, err = part.Write(audioBytes)
	if err != nil {
		return c.SendStatus(500)
	}

	writer.Close()

	// 3️⃣ Enviar a /calls/process-full
	req, err := http.NewRequest(
		"POST",
		"http://localhost:3000/calls/process-full",
		body,
	)
	if err != nil {
		return c.SendStatus(500)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	agentResp, err := client.Do(req)
	if err != nil {
		return c.SendStatus(500)
	}
	defer agentResp.Body.Close()

	replyAudio, err := io.ReadAll(agentResp.Body)
	if err != nil {
		return c.SendStatus(500)
	}

	// 4️⃣ Responder TwiML
	twiml := `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Play>` + string(replyAudio) + `</Play>
</Response>`

	c.Set("Content-Type", "application/xml")
	return c.SendString(twiml)
}
