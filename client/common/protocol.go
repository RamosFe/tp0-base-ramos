package common

import "encoding/binary"

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
