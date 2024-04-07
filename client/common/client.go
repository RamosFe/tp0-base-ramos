package common

import (
	"bufio"
	"net"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	id     uint8
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(id uint8, config ClientConfig) *Client {
	client := &Client{
		config: config,
		id:     id,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop sends a single message to the client
func (c *Client) StartClientLoop(betScanner *bufio.Scanner, batchSize uint16) {
	// Create the connection to the server
	c.createClientSocket()
	batch := NewBatch(batchSize)

	// Get the bet ticket from environment variables
	for betScanner.Scan() {
		betTicketToSend, err := NewBetTicketFromStr(c.id, betScanner.Text())
		if err != nil {
			log.Errorf("action: get ticket | result: fail | error: %v", err)
			return
		}

		err = batch.addBetTicket(&betTicketToSend)
		// The batch is full
		if err != nil {
			sendBetBatch(c.conn, &batch)

			// Cleans the batch and add the bet
			batch.clean()
			batch.addBetTicket(&betTicketToSend)
		}
	}

	if !batch.isEmpty() {
		sendBetBatch(c.conn, &batch)
	}

	// Send End bet batches
	sendEndSendBet(c.conn)

	// Send close connection signal
	sendCloseConnection(c.conn)

	// Close the connection
	c.conn.Close()

	// TODO Delete
	time.Sleep(5 * time.Second)

	c.createClientSocket()
	result := sendRequestWinner(c.conn, c.id)
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(result))
	sendCloseConnection(c.conn)
	c.conn.Close()
}
