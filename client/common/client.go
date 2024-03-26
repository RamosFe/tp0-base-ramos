package common

import (
	"net"
	"os"
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
func (c *Client) StartClientLoop(signalChan chan os.Signal) {
	// Create the connection to the server
	c.createClientSocket()

	// Get the bet ticket from environment variables
	betTicketToSend, err := NewBetTicketFromEnv()
	if err != nil {
		log.Errorf("action: get ticket | result: fail | error: %v", err)
		return
	}

	// Send bet ticket
	sendBet(c.conn, &betTicketToSend)

	// Close the connection
	c.conn.Close()
}
