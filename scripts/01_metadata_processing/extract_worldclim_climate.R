# Extract WorldClim climate variables for Legionella soil metadata
# Input:  metadata_coord.csv
# Output: metadata_coord_with_worldclim.csv

library(terra)
library(dplyr)
library(readr)

# -----------------------------
# User settings
# -----------------------------

metadata_file <- "metadata_coord.csv"

# Update these paths to wherever your unzipped WorldClim folders are
tavg_dir <- "/Users/hanssingh/Downloads/wc2.1_30s_tavg"
prec_dir <- "/Users/hanssingh/Downloads/wc2.1_30s_prec"

tmin_2016_2018_dir <- "/Users/hanssingh/Downloads/wc2.1_cruts4.09_2.5m_tmin_2010-2019"
tmax_2016_2018_dir <- "/Users/hanssingh/Downloads/wc2.1_cruts4.09_2.5m_tmax_2010-2019"
prec_2016_2018_dir <- "/Users/hanssingh/Downloads/wc2.1_cruts4.09_2.5m_prec_2010-2019"

output_file <- "metadata_coord_with_worldclim.csv"

# -----------------------------
# Load metadata
# -----------------------------

metadata <- read_csv(metadata_file, na = c("NA", ""))

metadata <- metadata %>%
  mutate(
    Collection_Date_parsed = as.Date(Collection_Date, format = "%m/%d/%y"),
    collection_month = as.integer(format(Collection_Date_parsed, "%m")),
    midrange_temp_C = NA_real_,
    annual_precip_mm = NA_real_
  )

# -----------------------------
# Case 1: exact collection dates
# -----------------------------

exact_rows <- which(metadata$climate_method == "exact")

for (m in 1:12) {
  message("Processing exact-date samples for month: ", m)
  
  rows_m <- exact_rows[metadata$collection_month[exact_rows] == m]
  
  if (length(rows_m) > 0) {
    month_code <- sprintf("%02d", m)
    
    # Monthly average temperature for collection month
    tavg_file <- file.path(tavg_dir, paste0("wc2.1_30s_tavg_", month_code, ".tif"))
    tavg_raster <- rast(tavg_file)
    
    pts <- metadata[rows_m, c("lon", "lat")]
    vals <- terra::extract(tavg_raster, pts, method = "bilinear")
    
    metadata$midrange_temp_C[rows_m] <- vals[, 2]
  }
}

# Annual precipitation from climatological monthly rasters
message("Processing annual precipitation for exact-date samples")

prec_files <- file.path(
  prec_dir,
  paste0("wc2.1_30s_prec_", sprintf("%02d", 1:12), ".tif")
)

prec_stack <- rast(prec_files)

pts_exact <- metadata[exact_rows, c("lon", "lat")]
prec_vals <- terra::extract(prec_stack, pts_exact, method = "bilinear")

metadata$annual_precip_mm[exact_rows] <- rowSums(
  prec_vals[, -1, drop = FALSE],
  na.rm = TRUE
)

# -----------------------------
# Case 2: samples collected across 2016–2018
# -----------------------------

range_rows <- which(metadata$climate_method == "range_2016_2018")

if (length(range_rows) > 0) {
  message("Processing 2016–2018 range-date samples")
  
  years <- 2016:2018
  months <- sprintf("%02d", 1:12)
  
  # Historical precipitation files
  prec_hist_files <- unlist(lapply(years, function(y) {
    file.path(
      prec_2016_2018_dir,
      paste0("wc2.1_cruts4.09_2.5m_prec_", y, "-", months, ".tif")
    )
  }))
  
  # Historical tmin files
  tmin_files <- unlist(lapply(years, function(y) {
    file.path(
      tmin_2016_2018_dir,
      paste0("wc2.1_cruts4.09_2.5m_tmin_", y, "-", months, ".tif")
    )
  }))
  
  # Historical tmax files
  tmax_files <- unlist(lapply(years, function(y) {
    file.path(
      tmax_2016_2018_dir,
      paste0("wc2.1_cruts4.09_2.5m_tmax_", y, "-", months, ".tif")
    )
  }))
  
  pts_range <- metadata[range_rows, c("lon", "lat")]
  
  # Annual precipitation = yearly totals averaged across 2016–2018
  prec_hist_stack <- rast(prec_hist_files)
  prec_hist_vals <- terra::extract(prec_hist_stack, pts_range, method = "bilinear")
  
  prec_matrix <- as.matrix(prec_hist_vals[, -1, drop = FALSE])
  
  prec_2016 <- rowSums(prec_matrix[, 1:12, drop = FALSE], na.rm = TRUE)
  prec_2017 <- rowSums(prec_matrix[, 13:24, drop = FALSE], na.rm = TRUE)
  prec_2018 <- rowSums(prec_matrix[, 25:36, drop = FALSE], na.rm = TRUE)
  
  metadata$annual_precip_mm[range_rows] <- rowMeans(
    cbind(prec_2016, prec_2017, prec_2018),
    na.rm = TRUE
  )
  
  # Midrange temperature = mean of ((tmin + tmax) / 2) across 2016–2018
  tmin_stack <- rast(tmin_files)
  tmax_stack <- rast(tmax_files)
  
  tmin_vals <- terra::extract(tmin_stack, pts_range, method = "bilinear")
  tmax_vals <- terra::extract(tmax_stack, pts_range, method = "bilinear")
  
  tmin_matrix <- as.matrix(tmin_vals[, -1, drop = FALSE])
  tmax_matrix <- as.matrix(tmax_vals[, -1, drop = FALSE])
  
  monthly_midrange <- (tmin_matrix + tmax_matrix) / 2
  
  metadata$midrange_temp_C[range_rows] <- rowMeans(
    monthly_midrange,
    na.rm = TRUE
  )
}

# -----------------------------
# Save output
# -----------------------------

write_csv(metadata, output_file)

message("Done. Output written to: ", output_file)