import { useState, useEffect, useRef } from 'react';
import { searchCompany } from '../services/api';

export default function CompanyDropdown({ searchText, onSelect }) {
    const [isOpen, setIsOpen] = useState(false);
    const [companies, setCompanies] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [manuallyClosed, setManuallyClosed] = useState(false);
    const debounceRef = useRef(null);

    useEffect(() => {
        // Reset manually closed state if text is cleared
        if (!searchText) {
            setManuallyClosed(false);
        }

        // Only search if length > 2
        if (!searchText || searchText.length < 2 || manuallyClosed) {
            setIsOpen(false);
            setCompanies([]);
            return;
        }

        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        debounceRef.current = setTimeout(async () => {
            setIsLoading(true);
            setIsOpen(true);
            try {
                const result = await searchCompany(searchText);
                setCompanies(result.companies || []);
            } catch (err) {
                console.error('Company search failed:', err);
                setCompanies([]);
            } finally {
                setIsLoading(false);
            }
        }, 300);

        return () => clearTimeout(debounceRef.current);
    }, [searchText, manuallyClosed]);

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
                ) : companies.length > 0 ? (
                    <div className="company-dropdown-list">
                        {companies.map((company, i) => (
                            <div
                                key={i}
                                className="company-dropdown-item"
                                onClick={() => {
                                    onSelect(company);
                                    setIsOpen(false);
                                }}
                            >
                                <span className="icon">🏢</span>
                                {company}
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
