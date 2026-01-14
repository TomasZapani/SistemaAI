package main

import (
	"log"
	"orquestator/actions"
	"orquestator/handlers"
	"os"

	"github.com/joho/godotenv"

	"github.com/gin-gonic/gin"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	// Load .env file
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file:", err)
	}

	actions.InitActions()

	r := gin.Default()

	// Handlers
	r.POST("/answer", handlers.AnswerHandler)
	r.POST("/gather", handlers.GatherHandler)
	r.POST("/error", handlers.ErrorHandler)

	ipListen := os.Getenv("HOST") + ":" + os.Getenv("PORT")

	if err := r.Run(ipListen); err != nil {
		log.Fatalf("failed to run server: %v", err)
	}
}
