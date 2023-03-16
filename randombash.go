//Stupid little script that pulls a quote from bash.org
package main

import (
	"fmt"
	"html"
	"io/ioutil"
	"math/rand"
	"net/http"
	"strings"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())

	resp, err := http.Get("http://bash.org/?random")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	quoteStart := strings.Index(string(body), "<p class=\"qt\">")
	if quoteStart == -1 {
		fmt.Println("Error: Quote not found")
		return
	}

	quoteEnd := strings.Index(string(body[quoteStart:]), "</p>")
	if quoteEnd == -1 {
		fmt.Println("Error: Quote not found")
		return
	}

	quoteHtml := string(body[quoteStart+len("<p class=\"qt\">") : quoteStart+quoteEnd])
	quoteText := html.UnescapeString(quoteHtml)
	quoteText = strings.TrimSpace(quoteText)

	fmt.Println(quoteText)
}
