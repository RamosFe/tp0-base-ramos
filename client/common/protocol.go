package common

import (
	"encoding/binary"
	log "github.com/sirupsen/logrus"
	"net"
)

const MaxBatchSize = 8192
const AckMsgSize = 1

type MessageType byte

const (
	SendBet         MessageType = 1
	EndSendBet      MessageType = 2
	CloseConnection MessageType = 3
)

type ByteConvertable interface {
	ToBytes() []byte
}

type Message struct {
	header  uint16
	payload []byte
}

type SendBetMessage struct {
	msgType MessageType
	msg     Message
}

type SignalMessage struct {
	msgType MessageType
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

func NewSendBetMessage(payload ByteConvertable) SendBetMessage {
	return SendBetMessage{
		msgType: SendBet,
		msg:     NewMessage(payload),
	}
}

func (m *SendBetMessage) ToBytes() []byte {
	buffer := []byte{byte(m.msgType)}
	msgBytes := m.msg.ToBytes()

	return append(buffer, msgBytes...)
}

func NewEndSendBetMessage() SignalMessage {
	return SignalMessage{
		msgType: EndSendBet,
	}
}

func NewCloseConnectionMessage() SignalMessage {
	return SignalMessage{
		msgType: CloseConnection,
	}
}

func (m *SignalMessage) ToBytes() []byte {
	return []byte{byte(m.msgType)}
}

func sendBetBatch(connection net.Conn, batch *BetTicketBatch) {
	// Create and send the message
	message := NewSendBetMessage(batch)
	err := writeToSocket(connection, message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}

	// Read acknowledgment message
	ackMesg := make([]byte, AckMsgSize)
	err = readFromSocket(connection, &ackMesg, AckMsgSize)
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

func sendEndSendBet(connection net.Conn) {
	message := NewEndSendBetMessage()
	err := writeToSocket(connection, message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}
}

func sendCloseConnection(connection net.Conn) {
	message := NewCloseConnectionMessage()
	err := writeToSocket(connection, message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return
	}
}
