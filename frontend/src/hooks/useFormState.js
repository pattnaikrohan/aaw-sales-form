import { useState, useCallback, useRef } from 'react';

const getInitialFormData = () => ({
    clientName: '',
    subject: '',
    method: '',
    purpose: '',
    status: '',
    primaryContact: '',
    actualDate: '',
    scheduledDate: new Date().toISOString().split('T')[0], /* Sets to today's YYYY-MM-DD */
    notes: '',
    submittedBy: '',
});

export default function useFormState() {
    const [formData, setFormData] = useState(getInitialFormData);
    const [autoFilledFields, setAutoFilledFields] = useState(new Set());
    const autoFillTimers = useRef({});

    const updateField = useCallback((name, value) => {
        setFormData((prev) => ({ ...prev, [name]: value }));
    }, []);

    const updateMultipleFields = useCallback((fieldMap) => {
        let newAutoFilled = new Set();
        
        setFormData((prev) => {
            const updated = { ...prev };
            for (const [key, value] of Object.entries(fieldMap)) {
                if (value !== undefined && value !== null && value !== '' && key in updated && prev[key] !== value) {
                    updated[key] = value;
                    newAutoFilled.add(key);
                }
            }
            return updated;
        });

        if (newAutoFilled.size > 0) {
            setAutoFilledFields((prev) => new Set([...prev, ...newAutoFilled]));

            for (const field of newAutoFilled) {
                if (autoFillTimers.current[field]) {
                    clearTimeout(autoFillTimers.current[field]);
                }
                autoFillTimers.current[field] = setTimeout(() => {
                    setAutoFilledFields((prev) => {
                        const next = new Set(prev);
                        next.delete(field);
                        return next;
                    });
                }, 2000);
            }
        }
    }, []);

    const resetForm = useCallback(() => {
        setFormData(getInitialFormData());
        setAutoFilledFields(new Set());
        // Clear all timers
        Object.values(autoFillTimers.current).forEach(clearTimeout);
        autoFillTimers.current = {};
    }, []);

    return {
        formData,
        updateField,
        updateMultipleFields,
        resetForm,
        autoFilledFields,
    };
}
