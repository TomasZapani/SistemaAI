package main

import (
	"log"
	"twilio-ai-agent-go/database"
	"twilio-ai-agent-go/handler"

	"github.com/joho/godotenv"

	"github.com/gin-gonic/gin"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file:", err)
	}

	err = database.InitDB()
	if err != nil {
		log.Fatal("Error connecting to DB:", err)
	}

	r := gin.Default()

	r.POST("/answer", handler.AnswerHandler)
	r.POST("/gather", handler.GatherHandler)
	r.POST("/error", handler.ErrorHandler)

	if err := r.Run("127.0.0.1:8080"); err != nil {
		log.Fatalf("failed to run server: %v", err)
	}
}
