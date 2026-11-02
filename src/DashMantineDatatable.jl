
module DashMantineDatatable
using Dash
using Pkg

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.1.0"

include("jl/''_dashmantinedatatable.jl")

function __init__()
# DUAL_MANTINE_BUNDLE_START
    function _datatable_bundle()
        major = 2
        for (_, dep) in Pkg.dependencies()
            if dep.name == "DashMantineComponents" && dep.version !== nothing
                major = dep.version.major
            end
        end
        return major >= 3 ? "dash_mantine_datatable.v9.min.js" : "dash_mantine_datatable.v8.min.js"
    end
    bundle = _datatable_bundle()
# DUAL_MANTINE_BUNDLE_END
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
    relative_package_path = bundle,
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = bundle * ".map",
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
