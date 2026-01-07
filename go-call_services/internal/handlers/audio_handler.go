package handlers

import (
	"bytes"
	"encoding/json"
	"io"
	"mime/multipart"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

func ReceiveAudio(c *fiber.Ctx) error {

	// 1. Obtener archivo enviado por el cliente
	fileHeader, err := c.FormFile("file")
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "file is required",
		})
	}

	file, err := fileHeader.Open()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error": "cannot open file",
		})
	}
	defer file.Close()

	// 2. Crear un buffer para reenviar el archivo a Python
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

	// 3. Enviar archivo al microservicio IA (Python)
	req, err := http.NewRequest("POST", "http://localhost:8000/ai/transcribe", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot connect to AI service"})
	}
	defer resp.Body.Close()

	// 4. Leer respuesta JSON del microservicio IA
	var aiResponse map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&aiResponse)

	// 5. Devolver la transcripción al cliente
	return c.JSON(fiber.Map{
		"status":        "audio processed",
		"transcription": aiResponse["text"],
	})
}
