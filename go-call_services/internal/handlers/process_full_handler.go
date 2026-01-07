package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

func ProcessFullCall(c *fiber.Ctx) error {

	// 1. Recibir audio
	fileHeader, err := c.FormFile("file")
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "file is required"})
	}

	file, err := fileHeader.Open()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot open file"})
	}
	defer file.Close()

	// 2. Enviar audio a /ai/transcribe
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, _ := writer.CreateFormFile("file", fileHeader.Filename)
	io.Copy(part, file)
	writer.Close()

	req, _ := http.NewRequest("POST", "http://localhost:8000/ai/transcribe", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "transcribe service unavailable"})
	}
	defer resp.Body.Close()

	var transcribeResp map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&transcribeResp)

	text := transcribeResp["text"].(string)
	log.Println("📝 Transcripción:", text)

	// 3. Enviar texto a /ai/reason
	reasonBody, _ := json.Marshal(map[string]interface{}{
		"message": text,
		"context": nil,
	})

	resp2, err := http.Post(
		"http://localhost:8000/ai/reason",
		"application/json",
		bytes.NewBuffer(reasonBody),
	)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "reason service unavailable"})
	}
	defer resp2.Body.Close()

	var reasonResp map[string]interface{}
	json.NewDecoder(resp2.Body).Decode(&reasonResp)

	reply := reasonResp["reply"].(string)
	notes := reasonResp["notes"]

	log.Println("🤖 Reply:", reply)

	// 4. Enviar reply a /ai/tts
	ttsBody, _ := json.Marshal(map[string]string{
		"text": reply,
	})

	resp3, err := http.Post(
		"http://localhost:8000/ai/tts",
		"application/json",
		bytes.NewBuffer(ttsBody),
	)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "tts service unavailable"})
	}
	defer resp3.Body.Close()

	audioBytes, err := io.ReadAll(resp3.Body)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot read audio"})
	}

	// 5. Devolver audio final + metadata en headers
	c.Set("Content-Type", "audio/mpeg")
	c.Set("X-Transcription", text)
	c.Set("X-Notes", fmt.Sprintf("%v", notes))

	return c.Send(audioBytes)
}
