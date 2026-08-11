import { useState, useEffect, useRef } from 'react';

export default function AutocompleteDropdown({ searchText, onSelect, fetchOptions, placeholder = "Search...", disabled = false }) {
    const [isOpen, setIsOpen] = useState(false);
    const [options, setOptions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [manuallyClosed, setManuallyClosed] = useState(false);
    const debounceRef = useRef(null);
    const lastSearchRef = useRef('');

    useEffect(() => {
        if (disabled) {
            setIsOpen(false);
            return;
        }

        // Reset manually closed state if text changes or is cleared
        if (searchText !== lastSearchRef.current) {
            setManuallyClosed(false);
            lastSearchRef.current = searchText;
        }

        // Only search if length >= 2
        if (!searchText || searchText.length < 2 || manuallyClosed) {
            setIsOpen(false);
            setOptions([]);
            return;
        }

        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        debounceRef.current = setTimeout(async () => {
            setIsLoading(true);
            setIsOpen(true);
            try {
                const result = await fetchOptions(searchText);
                // Assume result is an array of strings
                setOptions(result || []);
            } catch (err) {
                console.error('Search failed:', err);
                setOptions([]);
            } finally {
                setIsLoading(false);
            }
        }, 300);

        return () => clearTimeout(debounceRef.current);
    }, [searchText, manuallyClosed, fetchOptions, disabled]);

    if (!isOpen) return null;

    return (
        <div className="company-search-wrapper">
            <div className="company-dropdown">
                <button 
                    type="button" 
                    className="company-dropdown-close"
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsOpen(false);
                        setManuallyClosed(true);
                    }}
                    title="Close dropdown"
                >
                    ✕
                </button>
                {isLoading ? (
                    <div className="company-loading">
                        <span className="spinner spinner-sm"></span>
                        Searching...
                    </div>
                ) : options.length > 0 ? (
                    <div className="company-dropdown-list">
                        {options.map((option, i) => (
                            <div
                                key={i}
                                className="company-dropdown-item"
                                onClick={() => {
                                    onSelect(option);
                                    setIsOpen(false);
                                }}
                            >
                                {option}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="company-loading">No matches found</div>
                )}
            </div>
        </div>
    );
}
