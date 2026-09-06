package com.example.CrimeAi.fabric;

import org.springframework.context.annotation.Configuration;

@Configuration
public class FabricConfig {

    public static final String ORGANIZATIONS_PATH =
            "\\\\wsl.localhost\\Ubuntu\\home\\rohit7447\\EHR-Hyperledger-Fabric-Project\\fabric-samples\\test-network\\organizations";

    public static final String CHANNEL_NAME = "mychannel";

    public static final String CHAINCODE_NAME = "crimeai";

    public static final String MSP_ID = "Org1MSP";

    public static final String PEER_ENDPOINT = "localhost:7051";

    public static final String PEER_HOSTNAME =
            "peer0.org1.example.com";
}