// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CivicLandLeaseEngine
 * @dev Automated Municipal Land Leasing, Building Verification, and Purchase Engine.
 */
contract CivicLandLeaseEngine is Ownable {

    struct Parcel {
        uint256 parcelId;
        uint256 areaSqMeters;
        address currentTenant;
        uint256 monthlyRentWei;
        uint256 leaseStartTimestamp;
        uint256 constructionDeadline;
        bool isUtilitiesConnected;
        bool isBuildingVerified;
        bool isPurchased;
    }

    uint256 public totalParcels;
    address public municipalTreasury;

    mapping(uint256 => Parcel) public parcels;
    mapping(uint256 => mapping(address => uint256)) public rentPaidAccumulated;

    event ParcelRegistered(uint256 indexed parcelId, uint256 areaSqMeters, uint256 monthlyRentWei);
    event ParcelLeased(uint256 indexed parcelId, address indexed tenant, uint256 startTimestamp, uint256 deadline);
    event RentPaid(uint256 indexed parcelId, address indexed tenant, uint256 amount);
    event UtilitiesMarkedReady(uint256 indexed parcelId);
    event BuildingVerified(uint256 indexed parcelId, address indexed inspector);
    event TitleTransferred(uint256 indexed parcelId, address indexed newOwner);

    constructor(address _municipalTreasury) Ownable(msg.sender) {
        municipalTreasury = _municipalTreasury;
    }

    /**
     * @dev Register a new municipal plot in the system.
     */
    function registerParcel(uint256 areaSqMeters, uint256 monthlyRentWei) external onlyOwner {
        totalParcels++;
        parcels[totalParcels] = Parcel({
            parcelId: totalParcels,
            areaSqMeters: areaSqMeters,
            currentTenant: address(0),
            monthlyRentWei: monthlyRentWei,
            leaseStartTimestamp: 0,
            constructionDeadline: 0,
            isUtilitiesConnected: false,
            isBuildingVerified: false,
            isPurchased: false
        });

        emit ParcelRegistered(totalParcels, areaSqMeters, monthlyRentWei);
    }

    /**
     * @dev Tenant executes lease agreement for a plot.
     */
    function leaseParcel(uint256 parcelId, uint256 buildingTermYears) external payable {
        Parcel storage parcel = parcels[parcelId];
        require(parcel.currentTenant == address(0), "Parcel already leased");
        require(!parcel.isPurchased, "Parcel already owned");
        require(msg.value >= parcel.monthlyRentWei, "Insufficient initial rent payment");
        require(buildingTermYears >= 2 && buildingTermYears <= 5, "Term must be 2 to 5 years");

        parcel.currentTenant = msg.sender;
        parcel.leaseStartTimestamp = block.timestamp;
        parcel.constructionDeadline = block.timestamp + (buildingTermYears * 365 days);

        rentPaidAccumulated[parcelId][msg.sender] += msg.value;
        payable(municipalTreasury).transfer(msg.value);

        emit ParcelLeased(parcelId, msg.sender, block.timestamp, parcel.constructionDeadline);
    }

    /**
     * @dev Monthly rent collection routed directly to municipal treasury.
     */
    function payMonthlyRent(uint256 parcelId) external payable {
        Parcel storage parcel = parcels[parcelId];
        require(parcel.currentTenant == msg.sender, "Caller is not current tenant");
        require(!parcel.isPurchased, "Parcel is already fully purchased");

        rentPaidAccumulated[parcelId][msg.sender] += msg.value;
        payable(municipalTreasury).transfer(msg.value);

        emit RentPaid(parcelId, msg.sender, msg.value);
    }

    /**
     * @dev Municipal utility department confirms power/water/septic readiness.
     */
    function confirmUtilitiesConnected(uint256 parcelId) external onlyOwner {
        parcels[parcelId].isUtilitiesConnected = true;
        emit UtilitiesMarkedReady(parcelId);
    }

    /**
     * @dev Municipal building inspector approves completed construction.
     */
    function verifyBuildingCompletion(uint256 parcelId) external onlyOwner {
        Parcel storage parcel = parcels[parcelId];
        require(block.timestamp <= parcel.constructionDeadline, "Building deadline expired");
        require(parcel.isUtilitiesConnected, "Utilities must be verified first");
        
        parcel.isBuildingVerified = true;
        emit BuildingVerified(parcelId, msg.sender);
    }

    /**
     * @dev Execute final land purchase upon verified building completion (crediting rent).
     */
    function executeBuyout(uint256 parcelId, uint256 totalLandPriceWei) external payable {
        Parcel storage parcel = parcels[parcelId];
        require(parcel.currentTenant == msg.sender, "Only tenant can execute buyout");
        require(parcel.isBuildingVerified, "Building covenant not fulfilled");
        require(!parcel.isPurchased, "Title already transferred");

        uint256 credit = rentPaidAccumulated[parcelId][msg.sender];
        uint256 remainingBalance = totalLandPriceWei > credit ? totalLandPriceWei - credit : 0;

        require(msg.value >= remainingBalance, "Insufficient funds to settle remaining balance");

        parcel.isPurchased = true;
        payable(municipalTreasury).transfer(msg.value);

        emit TitleTransferred(parcelId, msg.sender);
    }
}
