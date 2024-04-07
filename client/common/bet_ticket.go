package common

import (
	"fmt"
	"strconv"
	"strings"
)

const (
	EnvNameField            = "NOMBRE"
	EnvSurnameField         = "APELLIDO"
	EnvDocumentField        = "DOCUMENTO"
	EnvBirthdayField        = "NACIMIENTO"
	EnvTicketNumberField    = "NUMERO"
	BetTicketFieldSeparator = ","
	BetTicketSeparator      = "|"
)

type BetTicket struct {
	name         string
	surname      string
	document     uint
	birthday     string
	ticketNumber uint
	agencyId     uint8
}

type BetTicketBatch struct {
	limit uint16
	data  []byte
	bets  []*BetTicket
}

func NewBatch(limit uint16) BetTicketBatch {
	return BetTicketBatch{
		limit: limit,
		data:  []byte{},
		bets:  []*BetTicket{},
	}
}

func (b *BetTicketBatch) addBetTicket(newBet *BetTicket) error {
	newBytesToAdd := newBet.ToBytes()
	if len(b.data) != 0 {
		newBytesToAdd = append([]byte(BetTicketSeparator), newBytesToAdd...)
	}

	if uint16(len(b.data)+len(newBytesToAdd)) > b.limit {
		return fmt.Errorf("exceded limit: %v", b.limit)
	}

	b.data = append(b.data, newBytesToAdd...)
	b.bets = append(b.bets, newBet)
	return nil
}

func (b *BetTicketBatch) isEmpty() bool {
	return len(b.data) == 0
}

func (b *BetTicketBatch) clean() {
	b.data = []byte{}
	b.bets = []*BetTicket{}
}

func (b BetTicketBatch) ToBytes() []byte {
	return b.data
}

func NewBetTicketFromStr(agencyId uint8, data string) (BetTicket, error) {
	splitData := strings.Split(data, ",")
	if len(splitData) != 5 {
		return BetTicket{}, fmt.Errorf("failed to parse data: %w", data)
	}

	document, err := strconv.ParseUint(splitData[2], 10, 32)
	if err != nil {
		return BetTicket{}, fmt.Errorf("failed to parse document: %w", err)
	}

	ticketNumber, err := strconv.ParseUint(splitData[4], 10, 32)
	if err != nil {
		return BetTicket{}, fmt.Errorf("failed to parse ticket number: %w", err)
	}

	return BetTicket{
		name:         splitData[0],
		surname:      splitData[1],
		document:     uint(document),
		birthday:     splitData[3],
		ticketNumber: uint(ticketNumber),
		agencyId:     agencyId,
	}, nil
}

func (b BetTicket) ToString() string {
	return b.name + BetTicketFieldSeparator +
		b.surname + BetTicketFieldSeparator +
		fmt.Sprint(b.document) + BetTicketFieldSeparator +
		b.birthday + BetTicketFieldSeparator +
		fmt.Sprint(b.ticketNumber) + BetTicketFieldSeparator +
		fmt.Sprint(b.agencyId)
}

func (b BetTicket) ToBytes() []byte {
	return []byte(b.ToString())
}
