import React, { useState } from 'react';

import { DataTable } from '../lib';

const records = [
    {
        id: 1,
        team: 'Ferrari',
        driver: 'Charles Leclerc',
        wins: 8,
        podiumRate: 72,
        country: 'Monaco',
        profileUrl: 'https://www.formula1.com/',
    },
    {
        id: 2,
        team: 'McLaren',
        driver: 'Lando Norris',
        wins: 5,
        podiumRate: 68,
        country: 'United Kingdom',
        profileUrl: 'https://www.formula1.com/',
    },
    {
        id: 3,
        team: 'Mercedes',
        driver: 'George Russell',
        wins: 3,
        podiumRate: 41,
        country: 'United Kingdom',
        profileUrl: 'https://www.formula1.com/',
    },
];

const App = () => {
    const [state, setState] = useState({
        page: 1,
        recordsPerPage: 10,
        sortStatus: { columnAccessor: 'driver', direction: 'asc' },
        selectedRecordIds: [1],
    });

    return (
        <div style={{ padding: 24 }}>
            <DataTable
                columns={[
                    { accessor: 'driver', sortable: true },
                    { accessor: 'team', sortable: true },
                    {
                        accessor: 'wins',
                        presentation: 'number',
                        sortable: true,
                        textAlign: 'right',
                    },
                    {
                        accessor: 'podiumRate',
                        title: 'Podium %',
                        presentation: 'progress',
                        sortable: true,
                    },
                    {
                        accessor: 'profileUrl',
                        title: 'Profile',
                        presentation: 'link',
                        hrefAccessor: 'profileUrl',
                        template: 'Open',
                    },
                ]}
                data={records}
                rowExpansion={{
                    content: {
                        type: 'fields',
                        title: '{driver}',
                        fields: [
                            { label: 'Country', accessor: 'country' },
                            { label: 'Wins', accessor: 'wins', presentation: 'number' },
                            { label: 'Team', accessor: 'team' },
                        ],
                    },
                }}
                selectionTrigger="checkbox"
                setProps={(nextProps) =>
                    setState((current) => ({ ...current, ...nextProps }))
                }
                {...state}
            />
        </div>
    );
};

export default App;
