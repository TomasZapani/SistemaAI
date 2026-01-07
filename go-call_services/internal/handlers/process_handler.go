package handlers

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"mime/multipart"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

func ProcessCall(c *fiber.Ctx) error {

	// 1. Obtener archivo enviado
	fileHeader, err := c.FormFile("file")
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "file is required"})
	}

	file, err := fileHeader.Open()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot open file"})
	}
	defer file.Close()

	// 2. Crear multipart para enviar a Python /ai/transcribe
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("file", fileHeader.Filename)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot create form file"})
	}

	_, err = io.Copy(part, file)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot copy file"})
	}

	writer.Close()

	// 3. Enviar audio a Python /ai/transcribe
	req, _ := http.NewRequest("POST", "http://localhost:8000/ai/transcribe", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot connect to AI service"})
	}
	defer resp.Body.Close()

	var transcribeResp map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&transcribeResp)

	text := transcribeResp["text"].(string)
	log.Println("📝 Transcripción:", text)

	// 4. Enviar transcripción a Python /ai/reason
	reasonBody, _ := json.Marshal(map[string]interface{}{
		"message": text,
		"context": nil,
	})

	resp2, err := http.Post("http://localhost:8000/ai/reason", "application/json", bytes.NewBuffer(reasonBody))
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot connect to AI reason service"})
	}
	defer resp2.Body.Close()

	var reasonResp map[string]interface{}
	json.NewDecoder(resp2.Body).Decode(&reasonResp)

	// 5. Devolver respuesta completa
	return c.JSON(fiber.Map{
		"transcription": text,
		"reply":         reasonResp["reply"],
		"notes":         reasonResp["notes"],
	})
}
