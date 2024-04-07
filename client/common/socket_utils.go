package common

import (
	"fmt"
	"io"
	"net"
)

func writeToSocket(connection net.Conn, msg []byte) error {
	sentData := 0
	for sentData < len(msg) {
		bytesSent, err := connection.Write(msg)
		if err != nil && err != io.ErrShortWrite {
			return fmt.Errorf("failed to send message: %v", msg)
		}

		sentData += bytesSent
	}

	return nil
}

func readFromSocket(connection net.Conn, buffer *[]byte, size int) error {
	recvData := 0
	internalBuffer := *buffer
	for recvData < size {
		bytesRecv, err := connection.Read(internalBuffer[recvData:])
		if err != nil {
			return fmt.Errorf("failed to recv message of size: %v", size)
		}

		recvData += bytesRecv
	}

	return nil
}
