package helper

import (
	"os"

	"github.com/twilio/twilio-go/twiml"
)

// End the call with a message
func EndCall(message string) (string, error) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceSay{
			Message:  message,
			Voice:    os.Getenv("TWILIO_VOICE"),
			Language: os.Getenv("TWILIO_LANGUAGE"),
		},
		&twiml.VoiceHangup{},
	})

	return twimlResult, err
}

// Use GatherCall to say something to the client and recive a speech transcription
func GatherCall(message string) (string, error) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceGather{
			Action:          os.Getenv("GATHER_ENDPOINT"),
			Language:        os.Getenv("TWILIO_LANGUAGE"),
			Input:           "speech",
			Enhanced:        "true",
			SpeechTimeout:   "auto",
			ProfanityFilter: "false",
			BargeIn:         "false",
			SpeechModel:     "experimental_conversations",
			InnerElements: []twiml.Element{
				&twiml.VoiceSay{
					Message:  message,
					Voice:    os.Getenv("TWILIO_VOICE"),
					Language: os.Getenv("TWILIO_LANGUAGE"),
				},
			},
		},
	})

	return twimlResult, err
}
