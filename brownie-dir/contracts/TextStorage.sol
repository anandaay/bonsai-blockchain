// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract TextStorage {
    string public stored_text;

    event TextChanged(string newText);

    constructor() {
        setText('Constructor Text, default value when contract has been deployed.');
    }

    function setText(string memory _text) public {
        stored_text = _text;
        emit TextChanged(_text); 
    }

    function getText() view public returns (string memory) {
        return stored_text;
    }

    
}