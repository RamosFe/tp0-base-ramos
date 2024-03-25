package common

import (
	"fmt"
	"os"
	"strconv"
)

const (
	EnvNameField         = "NOMBRE"
	EnvSurnameField      = "APELLIDO"
	EnvDocumentField     = "DOCUMENTO"
	EnvBirthdayField     = "NACIMIENTO"
	EnvTicketNumberField = "NUMERO"
)

type BetTicket struct {
	name         string
	surname      string
	document     uint
	birthday     string
	ticketNumber uint
}

func NewBetTicketFromEnv() (BetTicket, error) {
	name := os.Getenv(EnvNameField)
	surname := os.Getenv(EnvSurnameField)
	documentStr := os.Getenv(EnvDocumentField)
	birthdayStr := os.Getenv(EnvBirthdayField)
	ticketNumberStr := os.Getenv(EnvTicketNumberField)

	document, err := strconv.ParseUint(documentStr, 10, 32)
	if err != nil {
		return BetTicket{}, fmt.Errorf("failed to parse document: %w", err)
	}

	ticketNumber, err := strconv.ParseUint(ticketNumberStr, 10, 32)
	if err != nil {
		return BetTicket{}, fmt.Errorf("failed to parse ticket number: %w", err)
	}

	return BetTicket{
		name:         name,
		surname:      surname,
		document:     uint(document),
		birthday:     birthdayStr,
		ticketNumber: uint(ticketNumber),
	}, nil
}

func (b BetTicket) ToString() string {
	return b.name + "," +
		b.surname + "," +
		fmt.Sprint(b.document) + "," +
		b.birthday + "," +
		fmt.Sprint(b.ticketNumber)
}

func (b BetTicket) ToBytes() []byte {
	return []byte(b.ToString())
}
