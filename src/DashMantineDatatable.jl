
module DashMantineDatatable
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.1.0"

include("jl/''_dashmantinedatatable.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "dash_mantine_datatable",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "async-DashMantineDatatable.js",
    external_url = "https://unpkg.com/dash_mantine_datatable@0.1.0/dash_mantine_datatable/async-DashMantineDatatable.js",
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-DashMantineDatatable.js.map",
    external_url = "https://unpkg.com/dash_mantine_datatable@0.1.0/dash_mantine_datatable/async-DashMantineDatatable.js.map",
    dynamic = true,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_mantine_datatable.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_mantine_datatable.min.js.map",
    external_url = nothing,
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
