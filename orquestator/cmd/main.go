package main

import (
	"log"
	"orquestator/actions"
	"orquestator/handlers"

	"github.com/joho/godotenv"

	"github.com/gin-gonic/gin"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file:", err)
	}

	actions.InitActions()

	r := gin.Default()

	r.POST("/answer", handlers.AnswerHandler)
	r.POST("/gather", handlers.GatherHandler)
	r.POST("/error", handlers.ErrorHandler)

	if err := r.Run("127.0.0.1:8080"); err != nil {
		log.Fatalf("failed to run server: %v", err)
	}
}
