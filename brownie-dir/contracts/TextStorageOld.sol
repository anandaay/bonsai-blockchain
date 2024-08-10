// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract TextStorageOld {
    string public stored_text;

    constructor() {
        setText('constructor text');
    }

    function setText(string memory _text) public {
        stored_text = _text;
    }

    function getText() view public returns (string memory) {
        return stored_text;
    }
}