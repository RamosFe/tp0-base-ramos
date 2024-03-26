package common

import (
	"encoding/binary"
	log "github.com/sirupsen/logrus"
	"net"
	"strings"
)

const MaxBatchSize = 8192
const AckMsgSize = 1
const MsgTypeSize = 2
const HeaderSize = 2

type MsgType uint16

const (
	BetMsg    MsgType = 1
	EndMsg    MsgType = 2
	WinnerMsg MsgType = 3
)

type ByteConvertable interface {
	ToBytes() []byte
}

type Message struct {
	msgType MsgType
	header  uint16
	payload []byte
}

type EndMessage struct {
	msgType MsgType
}

func NewEndMessage() EndMessage {
	return EndMessage{
		msgType: EndMsg,
	}
}

func NewMessage(payload ByteConvertable) Message {
	payloadBytes := payload.ToBytes()
	return Message{
		msgType: BetMsg,
		header:  uint16(len(payloadBytes)),
		payload: payloadBytes,
	}
}

func (m *Message) ToBytes() []byte {
	msgTypeBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(msgTypeBytes, uint16(m.msgType))

	headerBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(headerBytes, m.header)

	return append(append(msgTypeBytes, headerBytes...), m.payload...)
}

func (m *EndMessage) ToBytes() []byte {
	msgTypeBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(msgTypeBytes, uint16(m.msgType))

	return msgTypeBytes
}

func sendBet(connection net.Conn, ticket *BetTicket) {
	// Create and send the message
	message := NewMessage(ticket)
	_, err := connection.Write(message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}

	// Read acknowledgment message
	ackMesg := make([]byte, AckMsgSize)
	_, err = connection.Read(ackMesg)
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

func sendBetBatch(connection net.Conn, batch *BetTicketBatch) {
	// Create and send the message
	message := NewMessage(batch)
	_, err := connection.Write(message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}

	// Read acknowledgment message
	ackMesg := make([]byte, AckMsgSize)
	_, err = connection.Read(ackMesg)
	if err != nil {
		log.Errorf("action: receive_ack | result: fail | error: %v", err)
		return
	} else {
		for _, ticket := range batch.bets {
			log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
				ticket.document,
				ticket.ticketNumber,
			)
		}
	}
}

func sendEndMsg(connection net.Conn) {
	message := NewEndMessage()
	_, err := connection.Write(message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}
}

func readWinners(connection net.Conn) []string {
	// Read Msg Type
	msgType := make([]byte, MsgTypeSize)
	_, err := connection.Read(msgType)
	if err != nil {
		log.Errorf("action: recive_winners | result: fail | error %v", err)
	}

	msgTypeValue := binary.BigEndian.Uint16(msgType)

	if msgTypeValue != uint16(WinnerMsg) {
		log.Errorf("action: recive_winners | result: fail | error expected %v got  %v", WinnerMsg, msgTypeValue)
	}

	// Read header
	msgHeader := make([]byte, HeaderSize)
	_, err = connection.Read(msgHeader)
	if err != nil {
		log.Errorf("action: recive_winners | result: fail | error %v", err)
	}

	msgHeaderValue := binary.BigEndian.Uint16(msgHeader)

	// Read payload
	msgPayload := make([]byte, msgHeaderValue)
	_, err = connection.Read(msgPayload)
	if err != nil {
		log.Errorf("action: recive_winners | result: fail | error %v", err)
	}
	payloadData := string(msgPayload[:])
	return strings.Split(payloadData, ",")
}
