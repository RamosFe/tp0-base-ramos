package common

import (
	"encoding/binary"
	"fmt"
	log "github.com/sirupsen/logrus"
	"net"
	"strings"
)

const MaxBatchSize = 8192
const HeaderSize = 2
const AckMsgSize = 1
const MsgTypeSize = 1

var NotAvailableWinnersErr error = fmt.Errorf("not available winners")

type MessageType byte

const (
	SendBet           MessageType = 1
	EndSendBet        MessageType = 2
	CloseConnection   MessageType = 3
	RequestWinner     MessageType = 4
	UnavailableWinner MessageType = 5
	AvailableWinner   MessageType = 6
)

type ByteConvertable interface {
	ToBytes() []byte
}

type Message struct {
	header  uint16
	payload []byte
}

type PayloadMessage struct {
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

func NewSendBetMessage(payload ByteConvertable) PayloadMessage {
	return PayloadMessage{
		msgType: SendBet,
		msg:     NewMessage(payload),
	}
}

func NewRequestWinnersMessage(payload ByteConvertable) PayloadMessage {
	return PayloadMessage{
		msgType: RequestWinner,
		msg:     NewMessage(payload),
	}
}

func (m *PayloadMessage) ToBytes() []byte {
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

func sendRequestWinner(connection net.Conn, agencyId byte) ([]string, error) {
	message := NewRequestWinnersMessage(NewWinnerRequest(agencyId))
	err := writeToSocket(connection, message.ToBytes())
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v", err)
		return nil, err
	}

	// Read response message type
	msgType := make([]byte, MsgTypeSize)
	err = readFromSocket(connection, &msgType, MsgTypeSize)
	if err != nil {
		log.Errorf("action: receive_winners | result: fail | error: %v", err)
		return nil, err
	}

	if msgType[0] == byte(AvailableWinner) {
		// Read header
		msgHeader := make([]byte, HeaderSize)
		err = readFromSocket(connection, &msgHeader, HeaderSize)
		if err != nil {
			log.Errorf("action: recive_winners | result: fail | error %v", err)
			return nil, err
		}

		msgHeaderValue := binary.BigEndian.Uint16(msgHeader)

		// Read payload
		msgPayload := make([]byte, msgHeaderValue)
		err = readFromSocket(connection, &msgPayload, int(msgHeaderValue))
		if err != nil {
			log.Errorf("action: recive_winners | result: fail | error %v", err)
			return nil, err
		}
		payloadData := string(msgPayload[:])
		listOfDocuments := strings.Split(payloadData, ",")
		var finalList []string

		for _, field := range listOfDocuments {
			if field != "" {
				finalList = append(finalList, field)
			}
		}

		return finalList, nil
	}

	if msgType[0] == byte(UnavailableWinner) {
		return nil, NotAvailableWinnersErr
	}

	return nil, fmt.Errorf("invalid msg type %v", msgType[0])
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
