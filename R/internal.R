# Bundle selection is reapplied by scripts/wire_dual_bundles.py after dash-generate-components.
.dashMantineDatatableBundle <- function() {
  candidates <- c("dashMantineComponents")
  for (name in candidates) {
    version <- tryCatch(
      as.character(utils::packageVersion(name)),
      error = function(...) NA_character_
    )
    if (!is.na(version)) {
      major <- suppressWarnings(as.integer(strsplit(version, ".", fixed = TRUE)[[1]][[1]]))
      if (!is.na(major) && major >= 3) {
        return("dash_mantine_datatable.v9.min.js")
      }
      return("dash_mantine_datatable.v8.min.js")
    }
  }
  "dash_mantine_datatable.v8.min.js"
}

.dashMantineDatatable_js_metadata <- function() {
deps_metadata <- list(`dash_mantine_datatable` = structure(list(name = "dash_mantine_datatable",
version = "0.1.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = 'async-DashMantineDatatable.js',
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashMantineDatatable",
all_files = FALSE, async = TRUE), class = "html_dependency"),
`dash_mantine_datatable` = structure(list(name = "dash_mantine_datatable",
version = "0.1.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = 'async-DashMantineDatatable.js.map',
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashMantineDatatable",
all_files = FALSE, dynamic = TRUE), class = "html_dependency"),
`dash_mantine_datatable` = structure(list(name = "dash_mantine_datatable",
version = "0.1.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = .dashMantineDatatableBundle(),
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashMantineDatatable",
all_files = FALSE), class = "html_dependency"),
`dash_mantine_datatable` = structure(list(name = "dash_mantine_datatable",
version = "0.1.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = paste0(.dashMantineDatatableBundle(), '.map'),
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashMantineDatatable",
all_files = FALSE, dynamic = TRUE), class = "html_dependency"))
return(deps_metadata)
}
