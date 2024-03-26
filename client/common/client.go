package common

import (
	"bufio"
	"net"
	"strconv"
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
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
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
	var listOfDocuments []string

	// Get the bet ticket from environment variables
	for betScanner.Scan() {
		betTicketToSend, err := NewBetTicketFromStr(betScanner.Text())
		if err != nil {
			log.Errorf("action: get ticket | result: fail | error: %v", err)
			return
		}

		listOfDocuments = append(listOfDocuments, strconv.FormatInt(int64(betTicketToSend.document), 10))
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

	// Send end msg
	sendEndMsg(c.conn)

	// Recv winners
	winners := readWinners(c.conn)

	// Filter only the winnera of the agency
	var listOfWinnersByAgency []string
	for _, winner := range winners {
		isContained := false
		for _, elem := range listOfDocuments {
			if elem == winner {
				isContained = true
			}
		}
		if isContained {
			listOfWinnersByAgency = append(listOfWinnersByAgency, winner)
		}
	}

	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(listOfWinnersByAgency))

	// Close the connection
	c.conn.Close()
}
