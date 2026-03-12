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

const normalizeValue = (name, value) => {
    if (!value || typeof value !== 'string') return value;
    const val = value.trim().toUpperCase();

    if (name === 'method') {
        if (['PHN', 'MTG', 'EML', '1ST', 'FUP', 'SRV', 'TRV'].includes(val)) return val;
        if (val.includes('PHONE') || val.includes('CALL')) return 'PHN';
        if (val.includes('MEET')) return 'MTG';
        if (val.includes('EMAIL')) return 'EML';
        if (val.includes('FIRST')) return '1ST';
        if (val.includes('FOLLOW') || val.includes('FUP')) return 'FUP';
        if (val.includes('SERVICE')) return 'SRV';
        if (val.includes('PORT') || val.includes('VOLUME')) return 'TRV';
    }

    if (name === 'purpose') {
        if (['PBS', 'EBS', 'EFO', 'TRD'].includes(val)) return val;
        if (val.includes('NEW') || val.includes('PROSPECT')) return 'PBS';
        if (val.includes('EXISTING') && val.includes('FURTHER')) return 'EFO';
        if (val.includes('EXISTING')) return 'EBS';
        if (val.includes('TRADE') || val.includes('TRD')) return 'TRD';
    }

    if (name === 'status') {
        if (['SCH', 'COM', 'CAN', 'CUR', 'HOT', 'WRM', 'CLD'].includes(val)) return val;
        if (val.includes('SCHEDULE')) return 'SCH';
        if (val.includes('COMPLET')) return 'COM';
        if (val.includes('CANCEL')) return 'CAN';
        if (val.includes('EXISTING') || val.includes('CURRENT')) return 'CUR';
        if (val.includes('HOT')) return 'HOT';
        if (val.includes('WARM')) return 'WRM';
        if (val.includes('COLD')) return 'CLD';
    }

    return value;
};

export default function useFormState() {
    const [formData, setFormData] = useState(getInitialFormData);
    const [autoFilledFields, setAutoFilledFields] = useState(new Set());
    const autoFillTimers = useRef({});

    const updateField = useCallback((name, value) => {
        const normalized = normalizeValue(name, value);
        setFormData((prev) => ({ ...prev, [name]: normalized }));
    }, []);

    const updateMultipleFields = useCallback((fieldMap) => {
        let newAutoFilled = new Set();
        
        setFormData((prev) => {
            const updated = { ...prev };
            for (const [key, value] of Object.entries(fieldMap)) {
                if (value !== undefined && value !== null && value !== '' && key in updated) {
                    const normalized = normalizeValue(key, value);
                    if (prev[key] !== normalized) {
                        updated[key] = normalized;
                        newAutoFilled.add(key);
                    }
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
