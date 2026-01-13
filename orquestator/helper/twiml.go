package helper

import (
	"os"

	"github.com/twilio/twilio-go/twiml"
)

func EndCall(message string) (string, error) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceSay{
			Message:  message,
			Voice:    "Polly.Lupe-Generative",
			Language: "es-US",
		},
		&twiml.VoiceHangup{},
	})

	return twimlResult, err
}

func GatherCall(message string) (string, error) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceGather{
			Action:          os.Getenv("GATHER_ENDPOINT"),
			Language:        "es-US",
			Input:           "speech",
			Enhanced:        "true",
			SpeechTimeout:   "auto",
			ProfanityFilter: "false",
			BargeIn:         "false",
			SpeechModel:     "experimental_conversations",
			InnerElements: []twiml.Element{
				&twiml.VoiceSay{
					Message:  message,
					Voice:    "Polly.Lupe-Generative",
					Language: "es-US",
				},
			},
		},
	})

	return twimlResult, err
}
