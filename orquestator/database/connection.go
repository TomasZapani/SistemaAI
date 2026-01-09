package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"twilio-ai-agent-go/agent"
)

var db *sql.DB

func InitDB() error {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s",
		os.Getenv("DB_USER"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_HOST"),
		os.Getenv("DB_PORT"),
		os.Getenv("DB_NAME"),
	)

	log.Println(dsn)

	var err error
	db, err = sql.Open("mysql", dsn)
	if err != nil {
		return err
	}
	return db.Ping()
}

func GetOrCreateUser(name string, phone_number string) (int64, error) {
	var id int64
	querySearch := `SELECT id_usuario FROM negocio.Usuarios WHERE nombre = ? AND telefono = ?`
	err := db.QueryRow(querySearch, name, phone_number).Scan(&id)

	if err == sql.ErrNoRows {
		// Si no existe, lo insertamos
		queryInsert := `INSERT INTO negocio.Usuarios (nombre, telefono) VALUES (?, ?)`
		res, err := db.Exec(queryInsert, name, phone_number)
		if err != nil {
			return 0, err
		}
		return res.LastInsertId()
	}

	return id, err
}

func CreateAppointment(data *agent.AppointmentData, phoneNumber string) error {
	uID, err := GetOrCreateUser(data.Name, phoneNumber)
	if err != nil {
		return fmt.Errorf("Error on user: %v", err)
	}

	queryCita := `INSERT INTO negocio.Citas (id_usuario, fecha, hora, estado) VALUES (?, ?, ?, ?)`
	resCita, err := db.Exec(queryCita, uID, data.Date, data.Time, "Pendiente")
	if err != nil {
		return fmt.Errorf("error on appointment: %v", err)
	}

	cID, _ := resCita.LastInsertId()
	if data.Notes != "" {
		queryNota := `INSERT INTO negocio.Notas (id_cita, contenido) VALUES (?, ?)`
		_, err = db.Exec(queryNota, cID, data.Notes)
		if err != nil {
			return fmt.Errorf("error en nota: %v", err)
		}
	}

	fmt.Printf("Appointment created: Usuario ID: %d, Cita ID: %d\n", uID, cID)
	return nil
}
