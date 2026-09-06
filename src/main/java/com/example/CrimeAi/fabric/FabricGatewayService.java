package com.example.CrimeAi.fabric;
import org.hyperledger.fabric.client.identity.X509Identity;
import io.grpc.ChannelCredentials;
import io.grpc.Grpc;
import io.grpc.ManagedChannel;
import io.grpc.TlsChannelCredentials;

import org.hyperledger.fabric.client.Contract;
import org.hyperledger.fabric.client.Gateway;
import org.hyperledger.fabric.client.Network;
import org.hyperledger.fabric.client.identity.Identity;
import org.hyperledger.fabric.client.identity.Identities;
import org.hyperledger.fabric.client.identity.Signer;
import org.hyperledger.fabric.client.identity.Signers;

import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.PrivateKey;

@Service
public class FabricGatewayService {

    private Gateway gateway;
    private Contract contract;
    private ManagedChannel channel;

    public FabricGatewayService() throws Exception {
        initialize();
    }

    private void initialize() throws Exception {

        // =====================================================
        // ORGANIZATIONS PATH
        // =====================================================

        String organizationsPath =
                FabricConfig.ORGANIZATIONS_PATH;

        // =====================================================
        // TLS CERTIFICATE
        // =====================================================

        Path tlsCertPath = Path.of(
                organizationsPath,
                "peerOrganizations",
                "org1.example.com",
                "peers",
                "peer0.org1.example.com",
                "tls",
                "ca.crt"
        );

        // =====================================================
        // ADMIN CERTIFICATE
        // =====================================================

        Path certPath = Path.of(
                organizationsPath,
                "peerOrganizations",
                "org1.example.com",
                "users",
                "Admin@org1.example.com",
                "msp",
                "signcerts",
                "Admin@org1.example.com-cert.pem"
        );

        // =====================================================
        // PRIVATE KEY DIRECTORY
        // =====================================================

        Path keyDir = Path.of(
                organizationsPath,
                "peerOrganizations",
                "org1.example.com",
                "users",
                "Admin@org1.example.com",
                "msp",
                "keystore"
        );

        // =====================================================
        // FIND PRIVATE KEY
        // =====================================================

        Path privateKeyPath;

        try (var files = Files.list(keyDir)) {

            privateKeyPath = files
                    .filter(Files::isRegularFile)
                    .findFirst()
                    .orElseThrow(() ->
                            new IOException(
                                    "Private key not found in: " + keyDir
                            )
                    );
        }

        // =====================================================
        // CHECK REQUIRED FILES
        // =====================================================

        if (!Files.exists(tlsCertPath)) {
            throw new IOException(
                    "Fabric TLS certificate not found: "
                            + tlsCertPath
            );
        }

        if (!Files.exists(certPath)) {
            throw new IOException(
                    "Fabric identity certificate not found: "
                            + certPath
            );
        }

        if (!Files.exists(privateKeyPath)) {
            throw new IOException(
                    "Fabric private key not found: "
                            + privateKeyPath
            );
        }

        // =====================================================
        // PRINT CONFIGURATION
        // =====================================================

        System.out.println();
        System.out.println("=================================");
        System.out.println("Fabric Configuration");
        System.out.println("=================================");
        System.out.println("TLS Cert     : " + tlsCertPath);
        System.out.println("Identity Cert: " + certPath);
        System.out.println("Private Key  : " + privateKeyPath);
        System.out.println("Peer         : " + FabricConfig.PEER_ENDPOINT);
        System.out.println("MSP          : " + FabricConfig.MSP_ID);
        System.out.println("Channel      : " + FabricConfig.CHANNEL_NAME);
        System.out.println("Chaincode    : " + FabricConfig.CHAINCODE_NAME);
        System.out.println("=================================");

        // =====================================================
        // TLS CONNECTION
        // =====================================================

        ChannelCredentials credentials =
                TlsChannelCredentials.newBuilder()
                        .trustManager(tlsCertPath.toFile())
                        .build();

        channel = Grpc.newChannelBuilder(
                        FabricConfig.PEER_ENDPOINT,
                        credentials
                )
                .overrideAuthority(
                        FabricConfig.PEER_HOSTNAME
                )
                .build();

        // =====================================================
        // READ ADMIN CERTIFICATE
        // =====================================================

        String certificatePem =
                Files.readString(certPath);

        // =====================================================
        // CREATE FABRIC IDENTITY
        // =====================================================
        Identity identity =
                new X509Identity(
                        FabricConfig.MSP_ID,
                        Identities.readX509Certificate(certificatePem)
                );
        // =====================================================
        // READ PRIVATE KEY
        // =====================================================

        String privateKeyPem =
                Files.readString(privateKeyPath);

        PrivateKey privateKey =
                Identities.readPrivateKey(
                        privateKeyPem
                );

        // =====================================================
        // CREATE SIGNER
        // =====================================================

        Signer signer =
                Signers.newPrivateKeySigner(
                        privateKey
                );

        // =====================================================
        // CREATE FABRIC GATEWAY
        // =====================================================

        gateway =
                Gateway.newInstance()
                        .identity(identity)
                        .signer(signer)
                        .connection(channel)
                        .connect();

        // =====================================================
        // GET NETWORK
        // =====================================================

        Network network =
                gateway.getNetwork(
                        FabricConfig.CHANNEL_NAME
                );

        // =====================================================
        // GET CHAINCODE CONTRACT
        // =====================================================

        contract =
                network.getContract(
                        FabricConfig.CHAINCODE_NAME
                );

        // =====================================================
        // SUCCESS
        // =====================================================

        System.out.println();
        System.out.println("=================================");
        System.out.println("Fabric Gateway Connected Successfully");
        System.out.println("=================================");
        System.out.println(
                "Channel  : "
                        + FabricConfig.CHANNEL_NAME
        );
        System.out.println(
                "Chaincode: "
                        + FabricConfig.CHAINCODE_NAME
        );
        System.out.println("=================================");
        System.out.println();

    }

    // =========================================================
    // CREATE AUDIT
    // =========================================================

    public String createAudit(
            String caseId,
            String action,
            String performedBy,
            String timestamp,
            String dataHash
    ) {

        try {

            byte[] result =
                    contract.submitTransaction(
                            "CreateAudit",
                            caseId,
                            action,
                            performedBy,
                            timestamp,
                            dataHash
                    );

            return new String(
                    result,
                    StandardCharsets.UTF_8
            );

        } catch (Exception e) {

            throw new RuntimeException(
                    "Failed to create Fabric audit: "
                            + e.getMessage(),
                    e
            );
        }
    }

    // =========================================================
    // GET CASE AUDITS
    // =========================================================

    public String getCaseAudits(
            String caseId
    ) {

        try {

            byte[] result =
                    contract.evaluateTransaction(
                            "GetCaseAudits",
                            caseId
                    );

            return new String(
                    result,
                    StandardCharsets.UTF_8
            );

        } catch (Exception e) {

            throw new RuntimeException(
                    "Failed to get Fabric audits: "
                            + e.getMessage(),
                    e
            );
        }
    }
}