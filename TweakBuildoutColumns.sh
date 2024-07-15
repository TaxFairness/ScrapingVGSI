#!/bin/bash

while IFS= read -r line
do
  echo "$line" |\
  sed 's/Max Lot Coverag/MaxLotCoverage/g' | \
  sed 's/Lot Coverage/LotCoverage/g' | \
  sed 's/Overall Rating/OverallRating/g' | \
  sed 's/Septic GPD Rating/SepticGPDRating/g' | \
  sed 's/Max Lot Cov Rating/MaxLotCovRating/g' | \
  sed 's/Road Frontage Rating/RoadFrontageRating/g' | \
  sed 's/Used Lot Cov Rating/UsedLotCovRating/g' | \
  sed 's/Parcel Area Rating/ParcelAreaRating/g' | \
  sed 's/New Units/NewUnits/g' | \
  sed 's/Conversion Units/ConversionUnits/g'

done