package common

import (
	"encoding/binary"
	log "github.com/sirupsen/logrus"
	"net"
)

const AckMsgSize = 1

type ByteConvertable interface {
	ToBytes() []byte
}

type Message struct {
	header  uint16
	payload []byte
}

func NewMessage(payload ByteConvertable) Message {
	payloadBytes := payload.ToBytes()
	return Message{
		header:  uint16(len(payloadBytes)),
		payload: payloadBytes,
	}
}

func (m *Message) ToBytes() []byte {
	headerBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(headerBytes, m.header)

	return append(headerBytes, m.payload...)
}

func sendBet(connection net.Conn, ticket *BetTicket) {
	// Create and send the message
	message := NewMessage(ticket)
	err := writeToSocket(connection, message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}

	// Read acknowledgment message
	ackMsg := make([]byte, AckMsgSize)
	err = readFromSocket(connection, &ackMsg, AckMsgSize)
	if err != nil {
		log.Errorf("action: receive_ack | result: fail | error: %v", err)
		return
	} else {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			ticket.document,
			ticket.ticketNumber,
		)
	}
}
