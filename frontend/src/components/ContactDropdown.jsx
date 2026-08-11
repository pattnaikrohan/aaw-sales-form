import { useState, useEffect, useRef } from 'react';
import { searchContact } from '../services/api';

export default function ContactDropdown({ searchText, clientName, onSelect }) {
    const [isOpen, setIsOpen] = useState(false);
    const [contacts, setContacts] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [manuallyClosed, setManuallyClosed] = useState(false);
    const debounceRef = useRef(null);
    const lastSearchRef = useRef('');

    useEffect(() => {
        // Reset manually closed state if text changes or is cleared
        if (searchText !== lastSearchRef.current) {
            setManuallyClosed(false);
            lastSearchRef.current = searchText;
        }

        // Only search if length > 2
        if (!searchText || searchText.length < 2 || manuallyClosed) {
            setIsOpen(false);
            setContacts([]);
            return;
        }

        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        debounceRef.current = setTimeout(async () => {
            setIsLoading(true);
            setIsOpen(true);
            try {
                // Must send clientName as well
                const result = await searchContact(searchText, clientName || '');
                setContacts(result.contacts || []);
            } catch (err) {
                console.error('Contact search failed:', err);
                setContacts([]);
            } finally {
                setIsLoading(false);
            }
        }, 300);

        return () => clearTimeout(debounceRef.current);
    }, [searchText, clientName, manuallyClosed]);

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
                ) : contacts.length > 0 ? (
                    <div className="company-dropdown-list">
                        {contacts.map((contact, i) => (
                            <div
                                key={i}
                                className="company-dropdown-item"
                                onClick={() => {
                                    onSelect(contact);
                                    setIsOpen(false);
                                }}
                            >
                                <span className="icon">👤</span>
                                {contact}
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
