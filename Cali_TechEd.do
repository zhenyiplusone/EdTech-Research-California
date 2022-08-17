program define clean
	keep if inrange(subgroupid, 1, 4) | inrange(subgroupid, 74, 80)

	drop if schoolcode == 0 | schoolcode == 9999999
	
	keep districtcode schoolcode testyear subgroupid studentstested grade testid meanscalescore
	
	order testyear, after(schoolcode)

	egen identifier = concat(testid subgroupid grade), punct("_")
	
	
	// Dropping the data if a school is in multiple districts for some reason, all of them have no score
	
	/*
	egen duplicateidentifier = concat(schoolcode identifier), punct("-")

	sort duplicateidentifier
	quietly by duplicateidentifier:  gen dup = cond(_N==1,0,_n)
	keep if dup == 0
	
	drop duplicateidentifier dup
	*/

	drop grade subgroupid testid

	// reshaping
	
	reshape wide studentstested meanscalescore, i(districtcode schoolcode) j(identifier) string

end 

import delimited "CAASPP/sb_ca2015_all_csv_v3.txt", clear
clean
destring, replace ignore("*")
save "cali.dta", replace

local filenamelist "CAASPP/sb_ca2016_all_csv_v3.txt CAASPP/sb_ca2017_all_csv_v2.txt CAASPP/sb_ca2018_all_csv_v3.txt CAASPP/sb_ca2019_all_csv_v4.txt"
display "`filenamelist'"

foreach filename in `filenamelist'{
	import delimited using `filename', clear
	clean
	destring, replace ignore("*")
	save "temp.dta", replace
	use cali.dta
	append using temp.dta
	save cali.dta, replace
}

use cali.dta, clear
// Getting the addresses
//gen schoolcodestr = string(schoolcode) 
gen districtcodestr = string(districtcode) 
//merge 1:1 schoolcodestr using SchoolDirectory.dta
merge m:1 districtcodestr using DistrictDirectory.dta
keep if _merge == 3
drop _merge

save cali_2.dta, replace

// Getting the funding information, need to update so it does so by year
import excel District_Mega_Sheet_2.xlsx, firstrow clear
save DistrictDetailedReport, replace

use cali_2.dta, clear
merge m:m DISTRICTADDRESSIDENTIFIER testyear using DistrictDetailedReport.dta
rename CommittedAmount DisCommittedAmount
rename CmtdTotalCost DisCmtdTotalCost
rename TotalAuthorizedDisbursement DisTotalAuthorizedDisbursement
rename _merge _districtmerge
save cali_3, replace

import excel District_Mega_Sheet_2.xlsx, firstrow clear
save DistrictDetailedReport, replace

use cali_4.dta, clear
merge m:m DISTRICTADDRESSIDENTIFIER testyear using DistrictDetailedReport.dta
rename CommittedAmount DisCommittedAmount
rename CmtdTotalCost DisCmtdTotalCost
rename TotalAuthorizedDisbursement DisTotalAuthorizedDisbursement
rename _merge _districtmerge
save cali_4, replace

import excel CASchoolSnapshot.xlsx, firstrow clear
save SchoolSnapshot, replace

import excel CASchoolDistrictEcon.xlsx, firstrow clear
save DistrictSnapshot, replace

use cali_4.dta, clear
merge 1:1 districtcode schoolcode testyear using SchoolSnapshot.dta
rename _merge _schoolsnapmerge

merge m:1 districtcode testyear using DistrictSnapshot.dta
rename _merge _districtsnapmerge

drop if _schoolsnapmerge == 2
drop if _districtsnapmerge == 2

save cali_5, replace
______

keep if grade == 3 | grade == 4 | grade == 5

keep if inrange(subgroupid, 1, 4) | inrange(subgroupid, 74, 80)

drop if schoolcode == 0

keep districtcode schoolcode testyear subgroupid studentstested grade testid meanscalescore

egen identifier = concat(testid subgroupid grade), punct("_")

drop grade subgroupid testid
/*
egen identifier = concat(schoolcode grade subgroupid testid), punct("-")

sort identifier
quietly by identifier:  gen dup = cond(_N==1,0,_n)
keep if dup != 0
*/


reshape wide studentstested meanscalescore, i(schoolcode) j(identifier) string

save cali_teched_1819_experimental_1, replace

import excel "CDESchoolDirectoryExport.xlsx", firstrow case(lower) clear
gen schoolcodestr = substr(cdscode, -7, 7)
replace schoolcodestr = usubinstr(schoolcodestr, "0", "", 1) 
split streetaddress
split streetzip, parse(-) generate(schoolzipsplit)
egen SCHOOLADDRESSIDENTIFIER = concat(schoolzipsplit1 streetaddress1), punct("-")
keep SCHOOLADDRESSIDENTIFIER schoolcodestr school
sort schoolcodestr
quietly by schoolcodestr:  gen dup = cond(_N==1,0,_n)
drop if dup > 1
drop dup
save SchoolDirectory, replace

import excel "CDEDistrictDirectoryExport - Copy.xlsx", firstrow case(lower) clear
gen districtcodestr = substr(cdscode, -12, 5)
split streetaddress
split streetzip, parse(-) generate(diszipsplit)
split district
gen districtfirst = lower(district1)
egen DISTRICTADDRESSIDENTIFIER = concat(districtfirst diszipsplit1 streetaddress1), punct("_")
keep DISTRICTADDRESSIDENTIFIER districtcodestr district
save DistrictDirectory, replace

use cali_teched_1819_experimental_1.dta
//gen schoolcodestr = string(schoolcode) 
gen districtcodestr = string(districtcode) 
//merge 1:1 schoolcodestr using SchoolDirectory.dta
merge m:1 districtcodestr using DistrictDirectory.dta
keep if _merge == 3
drop _merge

save cali_teched_1819_experimental_2, replace

import delimited using "DistrictDetailedReport2019.csv", clear
split applicantstreetaddress1
split billedentityname
gen billedentitynamefirst = lower(billedentityname1)
egen DISTRICTADDRESSIDENTIFIER = concat(billedentitynamefirst applicantzipcode applicantstreetaddress11), punct("-")
destring frncommittedamount, generate(districttotalfunded) ignore("$ ,%")
keep billedentityname districttotalfunded DISTRICTADDRESSIDENTIFIER
collapse (sum) districttotalfunded, by(billedentityname DISTRICTADDRESSIDENTIFIER)
save DistrictDetailedReport, replace

use cali_teched_1819_experimental_2.dta
merge m:1 DISTRICTADDRESSIDENTIFIER using DistrictDetailedReport.dta

save SchoolDirectory, replace

quietly ds, has(varlabel "*meanscalescore*" "*studentstested*")
local delete r(varlist)

foreach col in `r(varlist)'{
	destring `col', replace ignore(*)
}