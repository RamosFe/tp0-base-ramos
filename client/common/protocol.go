package common

import (
	"encoding/binary"
	log "github.com/sirupsen/logrus"
	"net"
)

const MaxBatchSize = 8192
const AckMsgSize = 1

type MsgType uint16

const (
	BetMsg MsgType = 1
	EndMsg MsgType = 2
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
