/**
 * Public entry point for the SDR++ custom card.
 *
 * Deploy this file to /local/rtl_dsr/card.js and register the Lovelace
 * resource as a "module".  The real implementation lives in
 * sdr-plus-plus-card.js and is re-exported here so the filename matches
 * the custom-card convention.
 */
export { default } from "./sdr-plus-plus-card.js";
