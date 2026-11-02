const React = require('react');

function jsx(type, props, key) {
    const config = props || {};
    const children = config.children;
    const nextProps = {};

    Object.keys(config).forEach((propName) => {
        if (propName !== 'children') {
            nextProps[propName] = config[propName];
        }
    });

    if (key !== undefined) {
        nextProps.key = key;
    }

    if (children === undefined) {
        return React.createElement(type, nextProps);
    }

    return React.createElement(type, nextProps, children);
}

module.exports = {
    Fragment: React.Fragment,
    jsx,
    jsxs: jsx,
};
