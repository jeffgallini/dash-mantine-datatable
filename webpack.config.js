const path = require('path');
const webpack = require('webpack');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

const mantineDatatableAliases = {
    '8': path.resolve(__dirname, 'node_modules/mantine-datatable'),
    '9': path.resolve(__dirname, 'node_modules/mantine-datatable-v9'),
};

module.exports = (env, argv) => {
    const mantineMajor = String((env && env.mantine) || '8');
    if (!Object.prototype.hasOwnProperty.call(mantineDatatableAliases, mantineMajor)) {
        throw new Error(
            `Unsupported Mantine major "${mantineMajor}". Pass --env mantine=8 or --env mantine=9.`
        );
    }

    let mode;

    const overrides = module.exports || {};

    // if user specified mode flag take that value
    if (argv && argv.mode) {
        mode = argv.mode;
    }

    // else if configuration object is already set (module.exports) use that value
    else if (overrides.mode) {
        mode = overrides.mode;
    }

    // else take webpack default (production)
    else {
        mode = 'production';
    }

    let filename = (overrides.output || {}).filename;
    if(!filename) {
        const modeSuffix = mode === 'development' ? 'dev' : 'min';
        filename = `${dashLibraryName}.v${mantineMajor}.${modeSuffix}.js`;
    }

    const entry = overrides.entry || {main: './src/lib/index.js'};

    const devtool = overrides.devtool || 'source-map';

    const externals = ('externals' in overrides) ? overrides.externals : ({
        react: 'React',
        'react-dom': 'ReactDOM',
        'plotly.js': 'Plotly',
        'prop-types': 'PropTypes',
        '@mantine/core': 'MantineCore',
        '@mantine/hooks': 'MantineHooks',
    });

    const bundlesMantine =
        overrides.externals === undefined &&
        Object.prototype.hasOwnProperty.call(overrides, 'externals');
    const datatablePackage = mantineDatatableAliases[mantineMajor];
    const alias = {
        'mantine-datatable$': datatablePackage,
        'mantine-datatable/styles.layer.css': path.join(
            datatablePackage,
            'dist',
            'styles.layer.css'
        ),
        'react/jsx-runtime': path.resolve(__dirname, 'src/lib/jsx-runtime-shim.js'),
        'react/jsx-dev-runtime': path.resolve(__dirname, 'src/lib/jsx-runtime-shim.js'),
    };
    if (bundlesMantine && mantineMajor === '9') {
        alias['@mantine/core'] = path.resolve(__dirname, 'node_modules/@mantine/core-v9');
        alias['@mantine/hooks'] = path.resolve(__dirname, 'node_modules/@mantine/hooks-v9');
    }

    return {
        mode,
        entry,
        resolve: {
            alias,
        },
        output: {
            path: path.resolve(__dirname, dashLibraryName),
            chunkFilename: '[name].js',
            filename,
            library: dashLibraryName,
            libraryTarget: 'window',
        },
        devtool,
        devServer: {
            static: {
                directory: path.join(__dirname, '/')
            }
        },
        externals,
        module: {
            rules: [
                {
                    test: /\.jsx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                    },
                },
                {
                    test: /\.css$/,
                    use: [
                        {
                            loader: 'style-loader',
                        },
                        {
                            loader: 'css-loader',
                        },
                    ],
                },
            ],
        },
        optimization: {
            splitChunks: {
                name: '[name].js',
                cacheGroups: {
                    async: {
                        chunks: 'async',
                        minSize: 0,
                        name(module, chunks, cacheGroupKey) {
                            return `${cacheGroupKey}-${chunks[0].name}`;
                        }
                    },
                    shared: {
                        chunks: 'all',
                        minSize: 0,
                        minChunks: 2,
                        name: 'dash_mantine_datatable-shared'
                    }
                }
            }
        },
        plugins: [
            new WebpackDashDynamicImport(),
            new webpack.SourceMapDevToolPlugin({
                filename: '[file].map',
                exclude: ['async-plotlyjs']
            })
        ]
    }
};
